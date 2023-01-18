from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup, DataGraphPopup, HistGraphPopup, ValvControlPopup
from pyModbusTCP.client import ModbusClient, WRITE_SINGLE_REGISTER
from timeseriesgraph import TimeSeriesGraph
from kivy.core.window import Window
from threading import Thread
from time import sleep
from datetime import datetime
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from random import random
from bdhandler import BDHandler
from kivy_garden.graph import LinePlot

class MainWidget(BoxLayout):
    _updateThread = None
    _updateWidget = True
    _tags = {}
    _tags_control = {}
    _max_points = 20
    _max_y = 5
    def __init__(self, scan_time, **kwargs):
        super().__init__()
        self._meas = {}
        self._meas['timestamp'] = None
        self._meas['values'] = {}
        self._meas_control = {}
        self._meas_control['timestamp'] = None
        self._meas_control['values'] = {}
        self._scan_time = scan_time
        self._serverIP = kwargs.get('server_ip')
        self._serverPort = kwargs.get('server_port')
        self._modbusClient = ModbusClient(host=self._serverIP, port=self._serverPort)
        self._modbusPopup = ModbusPopup(self._serverIP, self._serverPort)
        self._scanPopup = ScanPopup(self._scan_time)
        for key,addr in kwargs.get('modbus_addrs').items():
            plot_color = (random(),random(),random(),1)
            self._tags[key] = {'addr':addr,'color':plot_color}
        self._graphPopup = DataGraphPopup(self._max_points,self._max_y,self._tags['pressao']['color'])
        self._histPopup = HistGraphPopup(tags=self._tags)
        self._db = BDHandler(kwargs.get('db_path'),self._tags)
        for key2,addr2 in kwargs.get('control_addrs').items():
            self._tags_control[key2] = {'addr':addr2}
        self._controlPopup = ValvControlPopup()

    def startDataRead(self, ip, port):
        """
        Método para configuração do IP e porta do servidor Modbus
        Inicializa uma thread para leitura dos dados e atualização da interface
        """
        self._serverIP = ip
        self._serverPort = port
        self._modbusClient.host = self._serverIP
        self._modbusClient.port = self._serverPort
        # try:
        Window.set_system_cursor('wait')
        self._modbusClient.open()
        Window.set_system_cursor('arrow')
        if self._modbusClient.is_open:
            self._updateThread = Thread(target=self.updater)
            self._updateThread.start()
            self.ids.img_con.source = 'imgs/conectado.png'
            self._modbusPopup.dismiss()
        else:
            self._modbusPopup.setInfo('Falha na conexão com o servidor')
        # except Exception as e:
        #     print('Erro: ', e.args)

    def readData(self):
        """
        Método para leituras das datas do servidor
        """
        self._meas['timestamp'] = datetime.now()
        for key,value in self._tags.items():
            self._meas['values'][key] = self.readFloat(value['addr'])
        # print(self._meas)
    
    def readFloat(self,addr):
        result = self._modbusClient.read_holding_registers(addr,2)
        decoder = BinaryPayloadDecoder.fromRegisters(result,Endian.Big,Endian.Little)
        decoded = round(decoder.decode_32bit_float(),3)
        return decoded

    def readBit(self,addr):
        result = self._modbusClient.read_holding_registers(addr,1)
        decoder = BinaryPayloadDecoder.fromRegisters(result, Endian.Big)
        decoded = decoder.decode_16bit_int()
        result2 = [int(i) for i in list('{0:016b}'.format(decoded))]
        return result2

    def readControl(self):
        self._meas_control['timestamp'] = datetime.now()
        for key,value in self._tags_control.items():
            self._meas_control['values'][key] = self.readBit(value['addr'])
        bits_valv = self._meas_control['values']['valv']
        self.mudaCorValv(bits_valv)
        # print('Válvulas')
        # print(self._meas_control)

    def mudaCorValv(self,bits_valv):
        if bits_valv[-2] == 0:
            self.ids.valv2.color = (0,1,0,1)
        else:
            self.ids.valv2.color = (1,0,0,1)
        if bits_valv[-3] == 0:
            self.ids.valv3.color = (0,1,0,1)
        else:
            self.ids.valv3.color = (1,0,0,1)
        if bits_valv[-4] == 0:
            self.ids.valv4.color = (0,1,0,1)
        else:
            self.ids.valv4.color = (1,0,0,1)
        if bits_valv[-5] == 0:
            self.ids.valv5.color = (0,1,0,1)
        else:
            self.ids.valv5.color = (1,0,0,1)
        if bits_valv[-6] == 0:
            self.ids.valv6.color = (0,1,0,1)
        else:
            self.ids.valv6.color = (1,0,0,1)
    
    def writeValv(self,addr,text_valv):
        bits_valv = self._meas_control['values']['valv']
        # print(id_valv)
        num_valv = ((int(text_valv[-1])))*-1
        # print('Abrir '+text_valv[-1])
        if text_valv == ('Abrir '+text_valv[-1]):
            bits_valv[num_valv] = 0
        elif text_valv == ('Fechar '+text_valv[-1]):
            bits_valv[num_valv] = 1
        num16bits = int("".join(str(i) for i in bits_valv),2)
        # print(num_valv)
        # print(bits_valv)
        # print(num16bits)
        self._modbusClient.write_single_register(addr,num16bits)

    def updateGUI(self):
        """
        Método para atualização da interface gráfica em tempo real
        """
        # Atualização dos labels
        for key,value in self._tags.items():
            self.ids[key].text = str(self._meas['values'][key])
        # Atualização do gráfico
        self._graphPopup.ids.graph.updateGraph((self._meas['timestamp'],self._meas['values']['pressao']),0)

    def updater(self):
        """
        Método que invoca as rotinas de leitura de dados, atualização da interface e
        inserção dos dados no BD
        """
        try:
            while self._updateWidget:
                # ler os dados MODBUS
                self.readData()
                # atualizar interface
                self.updateGUI()
                # ler os dados de controle
                self.readControl()
                # inserir os dados no BD
                self._db.insertData(self._meas)
                sleep(self._scan_time/1000)
        except Exception as e:
            self._modbusClient.close()
            print('Erro: ', e.args)

    def stopRefresh(self):
        self._updateWidget = False
    
    def getDataDB(self):
        """
        Método que coleta as informações da interface fornecida pelo usuário e requisita a busca no BD
        """
        try:
            init_t = self.parseDTString(self._histPopup.ids.txt_init.text)
            final_t = self.parseDTString(self._histPopup.ids.txt_final.text)
            cols = []
            for sensor in self._histPopup.ids.sensores.children:
                if sensor.ids.checkbox.active:
                    cols.append(sensor.id)
            if init_t is None or final_t is None or len(cols)==0:
                return
            else:
                cols.append('timestamp')
                dados = self._db.selectData(cols,init_t,final_t)
                # print(dados)
            if dados is None or len(dados['timestamp'])==0:
                return
            
            self._histPopup.ids.graph.clearPlots()
            for key,value in dados.items():
                if key=='timestamp':
                    continue
                p = LinePlot(line_width=1.5,color=self._tags[key]['color'])
                p.points = [(x,value[x]) for x in range(len(value))]
                self._histPopup.ids.graph.add_plot(p)
            
            self._histPopup.ids.graph.xmax = len(dados[cols[0]])
            self._histPopup.ids.graph.update_x_labels([datetime.strptime(x,'%Y-%m-%d %H:%M:%S') for x in dados['timestamp']])
        except Exception as e:
            print('Erro: ', e.args)

    def parseDTString(self, date_string):
        """
        Método que converte a string de data em datetime
        """
        try:
            d = datetime.strptime(date_string, '%d/%m/%Y %H:%M:%S')
            return d.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print('Erro: ', e.args)
