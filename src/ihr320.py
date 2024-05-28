from pywinauto.application import Application
import time
import config

#pywinautoを使ってIHR320を操作するクラス
#IHR320のソフトウェア"MonoExample"がインストールされている必要がある

class ihr320:
    """
    Class to control the IHR320 software

    this class is indireclty controlling the IHR320 using IHR320 software with pywinauto.
    So, the IHR320 software should be installed in the computer.

    Attributes:
    app: pywinauto.application.Application object

    """
    """
    Control Identifiers:

Dialog - 'MonoExample'    (L685, T285, R1235, B755)
['MonoExampleDialog', 'MonoExample', 'Dialog']
child_window(title="MonoExample", class_name="#32770")
   |
   | ComboBox - 'IHR 320'    (L714, T382, R844, B402)
   | ['Which Mono?ComboBox', 'ComboBox', 'ComboBox0', 'ComboBox1']
   | child_window(title="IHR 320", class_name="ComboBox")
   |    |
   |    | Edit - 'IHR 320'    (L717, T385, R824, B399)
   |    | ['Which Mono?Edit', 'Edit', 'Edit0', 'Edit1']
   |    | child_window(title="IHR 320", class_name="Edit")
   |
   | Edit - 'IHR 320'    (L717, T385, R824, B399)
   | ['Which Mono?Edit', 'Edit', 'Edit0', 'Edit1']
   | child_window(title="IHR 320", class_name="Edit")
   |
   | Button - 'Initialize'    (L714, T416, R852, B448)
   | ['Initialize', 'Button', 'InitializeButton']
   | child_window(title="Initialize", class_name="Button")
   |
   | Edit - '0'    (L732, T499, R851, B522)
   | ['Edit2', 'PositionEdit']
   | child_window(title="0", class_name="Edit")
   |
   | ComboBox - ''    (L954, T500, R1105, B520)
   | ['ComboBox2', 'arbComboBox']
   | child_window(class_name="ComboBox")
   |    |
   |    | Edit - ''    (L957, T503, R1085, B517)
   |    | ['GratingEdit', 'Edit3']
   |    | child_window(class_name="Edit")
   |
   | Edit - ''    (L957, T503, R1085, B517)
   | ['GratingEdit', 'Edit3']
   | child_window(class_name="Edit")
   |
   | Edit - '0'    (L737, T605, R795, B634)
   | ['Edit4', 'FrontEdit', 'FrontEdit0', 'FrontEdit1']
   | child_window(title="0", class_name="Edit")
   |
   | Edit - '0'    (L819, T605, R877, B634)
   | ['Edit5', 'SideEdit', 'SideEdit0', 'SideEdit1']
   | child_window(title="0", class_name="Edit")
   |
   | Edit - '0'    (L737, T686, R795, B715)
   | ['Edit6', 'FrontEdit2']
   | child_window(title="0", class_name="Edit")
   |
   | Edit - '0'    (L819, T686, R877, B715)
   | ['Edit7', 'SideEdit2']
   | child_window(title="0", class_name="Edit")
   |
   | RadioButton - 'Axial'    (L998, T593, R1052, B625)
   | ['Axial', 'RadioButton', 'AxialRadioButton', 'RadioButton0', 'RadioButton1', 'Axial0', 'Axial1', 'AxialRadioButton0', 'AxialRadioButton1']
   | child_window(title="Axial", class_name="Button")
   |
   | RadioButton - 'Lateral'    (L1077, T593, R1154, B625)
   | ['LateralRadioButton', 'RadioButton2', 'Lateral', 'LateralRadioButton0', 'LateralRadioButton1', 'Lateral0', 'Lateral1']
   | child_window(title="Lateral", class_name="Button")
   |
   | RadioButton - 'Axial'    (L1000, T673, R1054, B705)
   | ['Axial2', 'RadioButton3', 'AxialRadioButton2']
   | child_window(title="Axial", class_name="Button")
   |
   | RadioButton - 'Lateral'    (L1064, T673, R1141, B705)
   | ['LateralRadioButton2', 'RadioButton4', 'Lateral2']
   | child_window(title="Lateral", class_name="Button")
   |
   | Static - 'Configure'    (L714, T334, R812, B348)
   | ['ConfigureStatic', 'Configure', 'Static', 'Static0', 'Static1']
   | child_window(title="Configure", class_name="Static")
   |
   | Static - 'Which Mono?'    (L714, T350, R831, B368)
   | ['Which Mono?Static', 'Static2', 'Which Mono?']
   | child_window(title="Which Mono?", class_name="Static")
   |
   | GroupBox - 'Communication Settings'    (L902, T341, R1203, B419)
   | ['Communication Settings', 'Communication SettingsGroupBox', 'GroupBox', 'GroupBox0', 'GroupBox1']      
   | child_window(title="Communication Settings", class_name="Button")
   |
   | Static - 'Type:'    (L917, T361, R963, B378)
   | ['Type:Static', 'Type:', 'Static3']
   | child_window(title="Type:", class_name="Static")
   |
   | Static - 'USB'    (L979, T361, R1084, B376)
   | ['USB', 'Static4', 'USBStatic']
   | child_window(title="USB", class_name="Static")
   |
   | Static - 'Port #:'    (L917, T379, R954, B394)
   | ['Port #:Static', 'Static5', 'Port #:']
   | child_window(title="Port #:", class_name="Static")
   |
   | Static - '257'    (L979, T379, R1068, B393)
   | ['Static6', '257', '257Static']
   | child_window(title="257", class_name="Static")
   |
   | GroupBox - 'Wavelength Control'    (L718, T464, R1208, B532)
   | ['Wavelength ControlGroupBox', 'Wavelength Control', 'GroupBox2']
   | child_window(title="Wavelength Control", class_name="Button")
   |
   | Static - 'Position'    (L734, T482, R844, B497)
   | ['Position', 'Static7', 'PositionStatic']
   | child_window(title="Position", class_name="Static")
   |
   | Static - 'arb'    (L861, T500, R952, B527)
   | ['arbStatic', 'Static8', 'arb', 'arbStatic0', 'arbStatic1', 'arb0', 'arb1']
   | child_window(title="arb", class_name="Static")
   |
   | Static - 'Grating'    (L961, T482, R1068, B500)
   | ['GratingStatic', 'Static9', 'Grating']
   | child_window(title="Grating", class_name="Static")
   |
   | GroupBox - 'Slits'    (L716, T550, R947, B733)
   | ['SlitsGroupBox', 'Slits', 'GroupBox3']
   | child_window(title="Slits", class_name="Button")
   |
   | GroupBox - 'Entrance'    (L728, T571, R933, B643)
   | ['EntranceGroupBox', 'GroupBox4', 'Entrance', 'EntranceGroupBox0', 'EntranceGroupBox1', 'Entrance0', 'Entrance1']
   | child_window(title="Entrance", class_name="Button")
   |
   | GroupBox - 'Exit'    (L728, T650, R933, B725)
   | ['GroupBox5', 'Exit', 'ExitGroupBox', 'Exit0', 'Exit1', 'ExitGroupBox0', 'ExitGroupBox1']
   | child_window(title="Exit", class_name="Button")
   |
   | Static - 'Front'    (L739, T590, R809, B607)
   | ['FrontStatic', 'Front', 'Static10', 'FrontStatic0', 'FrontStatic1', 'Front0', 'Front1']
   | child_window(title="Front", class_name="Static")
   | 
   | Static - 'Front'    (L735, T665, R805, B682)
   | ['FrontStatic2', 'Front2', 'Static11']
   | child_window(title="Front", class_name="Static")
   |
   | Static - 'Side'    (L821, T590, R891, B607)
   | ['Static12', 'Side', 'SideStatic', 'Side0', 'Side1', 'SideStatic0', 'SideStatic1']
   | child_window(title="Side", class_name="Static")
   |
   | Static - 'Side'    (L819, T662, R889, B679)
   | ['Static13', 'Side2', 'SideStatic2']
   | child_window(title="Side", class_name="Static")
   |
   | Static - 'arb'    (L889, T610, R921, B633)
   | ['arbStatic2', 'Static14', 'arb2']
   | child_window(title="arb", class_name="Static")
   |
   | Static - 'arb'    (L891, T691, R923, B714)
   | ['arbStatic3', 'Static15', 'arb3']
   | child_window(title="arb", class_name="Static")
   |
   | GroupBox - 'Mirrors'    (L970, T550, R1206, B733)
   | ['GroupBox6', 'Mirrors', 'MirrorsGroupBox']
   | child_window(title="Mirrors", class_name="Button")
   |
   | GroupBox - 'Entrance'    (L986, T571, R1191, B643)
   | ['EntranceGroupBox2', 'GroupBox7', 'Entrance2']
   | child_window(title="Entrance", class_name="Button")
   |
   | GroupBox - 'Exit'    (L984, T650, R1189, B725)
   | ['GroupBox8', 'Exit2', 'ExitGroupBox2']
   | child_window(title="Exit", class_name="Button")
   |
   | Static - 'Uninitialized'    (L917, T395, R1125, B418)
   | ['UninitializedStatic', 'Uninitialized', 'Static16']
   | child_window(title="Uninitialized", class_name="Static")
    """
    def __init__(self):
        self.app = Application(backend="win32").start(config.CCDMONOPATH, timeout=10)
        self.app["MonoExample"].wait(wait_for="enabled",timeout=20)
        print("IHR320 opened")
    
    def print(self):
        self.app["MonoExample"].print_control_identifiers()
    
    def Initialize(self):
        self.app["MonoExample"]["Button"].click()
        print("IHR320 initialized")
    
    def setmirrors(self, mirrors):
        self.app["MonoExample"]["Axial"].click()
        self.app["MonoExample"]["Axial2"].click()
        self.Initialize()
    
    def setallconfig(self, centerwavelength, grating, frontslit, sideslit=0):
        self.app["MonoExample"]["Axial"].click()
        self.app["MonoExample"]["Axial2"].click()
        self.app["MonoExample"]["PositionEdit"].set_text(str(centerwavelength))
        self.app["MonoExample"]["GratingEdit"].set_text(str(grating))
        self.app["MonoExample"]["FrontEdit"].set_text(str(frontslit))
        self.app["MonoExample"]["SideEdit"].set_text(str(sideslit))
        #self.Initialize()


if __name__ == "__main__":
    ihr = ihr320()
    ihr.Initialize()