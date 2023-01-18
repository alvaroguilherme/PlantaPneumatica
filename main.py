from kivy.app import App
from mainwidget import MainWidget
from kivy.lang.builder import Builder

class MainApp(App):
    """
    Classe com App
    """
    def build(self):
        # Externa
        # server_ip = '10.15.20.17'
        # port = 10014
        self._widget = MainWidget(scan_time=1000, server_ip='192.168.0.14', server_port=502,
        modbus_addrs = {
            'pressao':714,
            'vazao':716,
            'rpm':884,
            'torque':1420
        },
        control_addrs = {
            'valv':712
        },
        db_path = 'db/banco.db')
        return self._widget
    
    def on_stop(self):
        """
        Método que executa quando a aplicação é fechada
        """
        self._widget.stopRefresh()

if __name__ == '__main__':
    Builder.load_string(open('mainwidget.kv',encoding='utf8').read(),rulesonly=True)
    Builder.load_string(open('popups.kv',encoding='utf8').read(),rulesonly=True) 
    MainApp().run()