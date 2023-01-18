from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy_garden.graph import LinePlot
from kivy.uix.boxlayout import BoxLayout

class ModbusPopup(Popup):
    _info_lb = None
    def __init__(self, server_ip, server_port, **kwargs):
        super().__init__()
        self.ids.txt_ip.text = str(server_ip)
        self.ids.txt_port.text = str(server_port)

    def setInfo(self, message):
        self._info_lb = Label(text=message)
        self.ids.layout.add_widget(self._info_lb)
    
    def clearInfo(self):
        if self._info_lb is not None:
            self.ids.layout.remove_widget(self._info_lb)

class ScanPopup(Popup):
    def __init__(self, scan_time, **kwargs):
        super().__init__()
        self.ids.txt_st.text = str(scan_time)

class DataGraphPopup(Popup):
    def __init__(self, xmax, ymax, plot_color, **kwargs):
        super().__init__(**kwargs)
        self.plot = LinePlot(line_width=1.5,color=plot_color)
        self.ids.graph.add_plot(self.plot)
        self.ids.graph.xmax = xmax
        self.ids.graph.ymax = ymax

class LabeledCheckBoxHistGraph(BoxLayout):
    pass

class HistGraphPopup(Popup):
    def __init__(self, tags, **kwargs):
        super().__init__(**kwargs)
        for key,value in tags.items():
            cb = LabeledCheckBoxHistGraph()
            cb.ids.label.text = key
            cb.ids.label.color = value['color']
            cb.id = key
            self.ids.sensores.add_widget(cb)

class LabeledCheckBoxControl(BoxLayout):
    pass

class ValvControlPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)