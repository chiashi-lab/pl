from pywinauto.application import Application
import time
import os
import sys
sys.path.append('../')
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
    def __init__(self) -> None:
        self.app = Application(backend="win32").start(config.CCDMONOPATH, timeout=10)
        self.app["MonoExample"].wait(wait_for="enabled",timeout=20)
    
    def _print(self) -> None:
        print(self.app["MonoExample"].print_control_identifiers())
    
    def Initialize(self) -> None:
        self.app["MonoExample"]["Button"].click()
    
    def set_mirrors(self, mirrors) -> None:
        self.app["MonoExample"]["Axial"].click()
        self.app["MonoExample"]["Axial2"].click()
    
    def set_allconfig(self, centerwavelength:float, grating:float, frontslit:float, sideslit:float = 0.0) -> None:
        self.app["MonoExample"]["PositionEdit"].set_text(str(centerwavelength))
        self.app["MonoExample"]["GratingEdit"].set_text(str(grating))
        self.app["MonoExample"]["FrontEdit"].set_text(str(frontslit))
        self.app["MonoExample"]["FrontEdit"].type_keys("{ENTER}")
        self.app["MonoExample"]["SideEdit"].set_text(str(sideslit))

#pywinautoを使って検出器Symphonyを操作するクラス
#Symphonyのソフトウェア"MFC_CCDExample"がインストールされている必要がある

class Symphony:
    """
    Class to control the Symphony software

    this class is indireclty controlling the Symphony using Symphony software with pywinauto.
    So, the Symphony software should be installed in the computer.

    Attributes:
    app: pywinauto.application.Application object

    """
    """
    Dialog - 'MFC_CCDExample'    (L661, T276, R1260, B764)
['MFC_CCDExample', 'MFC_CCDExampleDialog', 'Dialog']
child_window(title="MFC_CCDExample", class_name="#32770")
   |
   | ComboBox - 'Symphony'    (L676, T325, R802, B345)
   | ['ComboBox', 'Device SelectionComboBox', 'ComboBox0', 'ComboBox1']
   | child_window(title="Symphony", class_name="ComboBox")
   |
   | Button - 'Connect'    (L834, T323, R911, B344)
   | ['Button', 'ConnectButton', 'Connect', 'Button0', 'Button1']
   | child_window(title="Connect", class_name="Button")
   |
   | Button - 'Initialize'    (L927, T325, R1004, B346)
   | ['Button2', 'Initialize', 'InitializeButton']
   | child_window(title="Initialize", class_name="Button")
   |
   | Edit - '0'    (L776, T377, R822, B395)
   | ['Integration Time:Edit', 'Edit', 'Edit0', 'Edit1']
   | child_window(title="0", class_name="Edit")
   |
   | ComboBox - ''    (L731, T400, R859, B420)
   | ['ComboBox2', 'GainComboBox']
   | child_window(class_name="ComboBox")
   |
   | ComboBox - ''    (L729, T428, R860, B448)
   | ['ADCComboBox', 'ComboBox3']
   | child_window(class_name="ComboBox")
   |
   | RadioButton - 'Spectra'    (L687, T466, R764, B483)
   | ['RadioButton', 'SpectraRadioButton', 'Spectra', 'RadioButton0', 'RadioButton1']
   | child_window(title="Spectra", class_name="Button")
   | 
   | RadioButton - 'Image'    (L778, T461, R859, B487)
   | ['RadioButton2', 'Image', 'ImageRadioButton']
   | child_window(title="Image", class_name="Button")
   |
   | Edit - '0'    (L955, T382, R1004, B400)
   | ['X StartEdit', 'Edit2']
   | child_window(title="0", class_name="Edit")
   |
   | Edit - '0'    (L955, T404, R1004, B422)
   | ['Y StartEdit', 'Edit3']
   | child_window(title="0", class_name="Edit")
   |
   | Edit - '0'    (L955, T430, R1004, B448)
   | ['X EndEdit', 'Edit4']
   | child_window(title="0", class_name="Edit")
   |
   | Edit - '0'    (L955, T455, R1004, B473)
   | ['Y EndEdit', 'Edit5']
   | child_window(title="0", class_name="Edit")
   |
   | Edit - '0'    (L955, T476, R1004, B494)
   | ['X BinEdit', 'Edit6']
   | child_window(title="0", class_name="Edit")
   |
   | Edit - '0'    (L955, T497, R1004, B515)
   | ['Y BinEdit', 'Edit7']
   | child_window(title="0", class_name="Edit")
   |
   | Button - 'Set Params'    (L685, T493, R757, B514)
   | ['Button3', 'Set ParamsButton', 'Set Params']
   | child_window(title="Set Params", class_name="Button")
   |
   | Button - 'Start Acq'    (L1151, T521, R1218, B547)
   | ['Button4', 'Start Acq', 'Start AcqButton']
   | child_window(title="Start Acq", class_name="Button")
   |
   | Button - 'Save Data'    (L900, T716, R1000, B746)
   | ['Button5', 'Save DataButton', 'Save Data']
   | child_window(title="Save Data", class_name="Button")
   |
   | Button - 'OK'    (L676, T724, R764, B745)
   | ['Button6', 'OK', 'OKButton']
   | child_window(title="OK", class_name="Button")
   |
   | Button - 'Cancel'    (L778, T724, R866, B745)
   | ['Button7', 'Cancel', 'CancelButton']
   | child_window(title="Cancel", class_name="Button")
   |
   | GroupBox - 'Device Selection'    (L668, T310, R1020, B355)
   | ['GroupBox', 'Device SelectionGroupBox', 'Device Selection', 'GroupBox0', 'GroupBox1']
   | child_window(title="Device Selection", class_name="Button")
   |
   | GroupBox - 'Setup'    (L669, T364, R1017, B522)
   | ['GroupBox2', 'SetupGroupBox', 'Setup']
   | child_window(title="Setup", class_name="Button")
   |
   | GroupBox - 'Acquire'    (L1030, T506, R1233, B743)
   | ['GroupBox3', 'AcquireGroupBox', 'Acquire']
   | child_window(title="Acquire", class_name="Button")
   |
   | Static - 'Integration Time:'    (L682, T379, R777, B394)
   | ['Static', 'Integration Time:Static', 'Integration Time:', 'Static0', 'Static1']
   | child_window(title="Integration Time:", class_name="Static")
   |
   | Static - 'Gain'    (L680, T404, R727, B418)
   | ['Gain', 'GainStatic', 'Static2']
   | child_window(title="Gain", class_name="Static")
   |
   | Static - '<units>'    (L830, T380, R867, B392)
   | ['Static3', '<units>Static', '<units>']
   | child_window(title="<units>", class_name="Static")
   | 
   | GroupBox - 'Info'    (L1030, T313, R1230, B504)
   | ['GroupBox4', 'InfoGroupBox', 'Info']
   | child_window(title="Info", class_name="Button")
   |
   | CheckBox - 'Temp'    (L1042, T331, R1103, B343)
   | ['CheckBox', 'Temp', 'TempCheckBox', 'CheckBox0', 'CheckBox1']
   | child_window(title="Temp", class_name="Button")
   |
   | Static - ''    (L1116, T331, R1170, B346)
   | ['Static4', 'TempStatic']
   | child_window(class_name="Static")
   |
   | Static - 'Chip X:'    (L1044, T380, R1084, B394)
   | ['Static5', 'Chip X:Static', 'Chip X:', 'Chip X:Static0', 'Chip X:Static1']
   | child_window(title="Chip X:", class_name="Static")
   |
   | Static - 'Chip Y:'    (L1044, T400, R1091, B414)
   | ['Chip Y:Static', 'Static6', 'Chip Y:', 'Chip Y:Static0', 'Chip Y:Static1']
   | child_window(title="Chip Y:", class_name="Static")
   |
   | Static - ''    (L1103, T380, R1191, B394)
   | ['Static7', 'Chip X:Static2']
   | child_window(class_name="Static")
   |
   | Static - ''    (L1103, T400, R1171, B417)
   | ['Chip Y:Static2', 'Static8']
   | child_window(class_name="Static")
   |
   | GroupBox - 'Acq Format'    (L678, T451, R885, B490)
   | ['GroupBox5', 'Acq FormatGroupBox', 'Acq Format']
   | child_window(title="Acq Format", class_name="Button")
   |
   | Static - 'X Start'    (L909, T383, R949, B398)
   | ['X Start', 'Static9', 'X StartStatic']
   | child_window(title="X Start", class_name="Static")
   |
   | Static - 'Y Start'    (L909, T406, R949, B421)
   | ['Static10', 'Y Start', 'Y StartStatic']
   | child_window(title="Y Start", class_name="Static")
   |
   | Static - 'X End'    (L909, T431, R949, B446)
   | ['Static11', 'X EndStatic', 'X End']
   | child_window(title="X End", class_name="Static")
   |
   | Static - 'Y End'    (L909, T457, R949, B472)
   | ['Static12', 'Y EndStatic', 'Y End']
   | child_window(title="Y End", class_name="Static")
   |
   | Static - 'X Bin'    (L909, T478, R949, B493)
   | ['X BinStatic', 'Static13', 'X Bin']
   | child_window(title="X Bin", class_name="Static")
   |
   | Static - 'Y Bin'    (L909, T499, R949, B514)
   | ['Static14', 'Y BinStatic', 'Y Bin']
   | child_window(title="Y Bin", class_name="Static")
   |
   | Static - 'ADC'    (L682, T431, R728, B446)
   | ['Static15', 'ADCStatic', 'ADC']
   | child_window(title="ADC", class_name="Static")
   |
   | Static - 'Status:'    (L1060, T554, R1106, B566)
   | ['Status:', 'Static16', 'Status:Static', 'Status:Static0', 'Status:Static1']
   | child_window(title="Status:", class_name="Static")
   |
   | Static - 'Update:'    (L1060, T611, R1116, B623)
   | ['Static17', 'Update:', 'Update:Static', 'Update:Static0', 'Update:Static1']
   | child_window(title="Update:", class_name="Static")
   |
   | Static - ''    (L1121, T554, R1219, B601)
   | ['Static18', 'Status:Static2']
   | child_window(class_name="Static")
   |
   | Static - ''    (L1119, T611, R1221, B641)
   | ['Static19', 'Update:Static2']
   | child_window(class_name="Static")
   |
   | Static - 'Firmware Version:'    (L1046, T421, R1167, B433)
   | ['Static20', 'Firmware Version:Static', 'Firmware Version:', 'Firmware Version:Static0', 'Firmware Version:Static1']
   | child_window(title="Firmware Version:", class_name="Static")
   |
   | Static - ''    (L1046, T437, R1179, B454)
   | ['Static21', 'Firmware Version:Static2']
   | child_window(class_name="Static")
   |
   | Static - 'Description:'    (L1046, T458, R1158, B472)
   | ['Static22', 'Description:', 'Description:Static', 'Description:Static0', 'Description:Static1']        
   | child_window(title="Description:", class_name="Static")
   |
   | Static - ''    (L1046, T475, R1193, B495)
   | ['Static23', 'Description:Static2']
   | child_window(class_name="Static")
   |
   | Static - 'Name:'    (L1044, T349, R1084, B363)
   | ['Name:Static', 'Static24', 'Name:', 'Name:Static0', 'Name:Static1']
   | child_window(title="Name:", class_name="Static")
   |
   | Static - ''    (L1096, T349, R1196, B379)
   | ['Name:Static2', 'Static25']
   | child_window(class_name="Static")
   |
   | GroupBox - 'Stream Acquisition'    (L676, T529, R1019, B642)
   | ['GroupBox6', 'Stream Acquisition', 'Stream AcquisitionGroupBox']
   | child_window(title="Stream Acquisition", class_name="Button")
   |
   | RadioButton - 'Simple Loop'    (L683, T544, R779, B559)
   | ['RadioButton3', 'Simple Loop', 'Simple LoopRadioButton']
   | child_window(title="Simple Loop", class_name="Button")
   |
   | RadioButton - 'Save to memory'    (L683, T560, R799, B575)
   | ['RadioButton4', 'Save to memory', 'Save to memoryRadioButton']
   | child_window(title="Save to memory", class_name="Button")
   |
   | RadioButton - 'Save to Files'    (L683, T577, R783, B592)
   | ['RadioButton5', 'Save to FilesRadioButton', 'Save to Files']
   | child_window(title="Save to Files", class_name="Button")
   |
   | Button - 'GO'    (L932, T541, R1007, B568)
   | ['Button8', 'GO', 'GOButton']
   | child_window(title="GO", class_name="Button")
   |
   | Static - 'Count:'    (L687, T598, R726, B610)
   | ['Static26', 'Count:Static', 'Count:']
   | child_window(title="Count:", class_name="Static")
   |
   | Static - 'FilePath:'    (L687, T622, R736, B634)
   | ['FilePath:Static', 'Static27', 'FilePath:']
   | child_window(title="FilePath:", class_name="Static")
   |
   | Edit - '1'    (L753, T595, R830, B613)
   | ['Count:Edit', 'Edit8']
   | child_window(title="1", class_name="Edit")
   |
   | Edit - 'c:\temp'    (L753, T617, R1007, B635)
   | ['FilePath:Edit', 'Edit9']
   | child_window(title="c:\temp", class_name="Edit")
   | 
   | Static - 'Time (sec):'    (L874, T584, R937, B596)
   | ['Static28', 'Time (sec):', 'Time (sec):Static', 'Time (sec):Static0', 'Time (sec):Static1']
   | child_window(title="Time (sec):", class_name="Static")
   |
   | Static - ''    (L946, T584, R1016, B596)
   | ['Static29', 'Time (sec):Static2']
   | child_window(class_name="Static")
   |
   | Static - 'Iteration:'    (L888, T601, R937, B613)
   | ['Static30', 'Iteration:Static', 'Iteration:', 'Iteration:Static0', 'Iteration:Static1']
   | child_window(title="Iteration:", class_name="Static")
   |
   | Static - ''    (L946, T601, R1016, B613)
   | ['Static31', 'Iteration:Static2']
   | child_window(class_name="Static")
   |
   | Static - 'Min'    (L1061, T656, R1094, B668)
   | ['MinStatic', 'Static32', 'Min', 'MinStatic0', 'MinStatic1']
   | child_window(title="Min", class_name="Static")
   |
   | Static - 'Max'    (L1061, T674, R1094, B686)
   | ['Static33', 'MaxStatic', 'Max', 'MaxStatic0', 'MaxStatic1']
   | child_window(title="Max", class_name="Static")
   |
   | Static - 'Avg'    (L1061, T692, R1094, B704)
   | ['Static34', 'AvgStatic', 'Avg', 'AvgStatic0', 'AvgStatic1']
   | child_window(title="Avg", class_name="Static")
   |
   | Static - 'StdDev'    (L1061, T712, R1112, B724)
   | ['Static35', 'StdDev', 'StdDevStatic', 'StdDevStatic0', 'StdDevStatic1']
   | child_window(title="StdDev", class_name="Static")
   |
   | Static - ''    (L1126, T655, R1228, B669)
   | ['MinStatic2', 'Static36']
   | child_window(class_name="Static")
   |
   | Static - ''    (L1126, T673, R1228, B687)
   | ['Static37', 'MaxStatic2']
   | child_window(class_name="Static")
   |
   | Static - ''    (L1126, T692, R1228, B706)
   | ['Static38', 'AvgStatic2']
   | child_window(class_name="Static")
   |
   | Static - ''    (L1126, T713, R1228, B727)
   | ['Static39', 'StdDevStatic2']
   | child_window(class_name="Static")
   |
   | Button - 'Triggers'    (L827, T655, R925, B678)
   | ['Button9', 'TriggersButton', 'Triggers', 'Triggers0', 'Triggers1']
   | child_window(title="Triggers", class_name="Button")
   |
   | CheckBox - 'Enabled'    (L710, T661, R850, B679)
   | ['CheckBox2', 'Enabled', 'EnabledCheckBox']
   | child_window(title="Enabled", class_name="Button")
   |
   | GroupBox - 'Triggers'    (L673, T643, R1002, B684)
   | ['GroupBox7', 'TriggersGroupBox', 'Triggers2']
   | child_window(title="Triggers", class_name="Button")
   |
   | CheckBox - 'HW Multi Acq'    (L802, T544, R911, B562)
   | ['CheckBox3', 'HW Multi Acq', 'HW Multi AcqCheckBox']
   | child_window(title="HW Multi Acq", class_name="Button")
   |
   | Static - ''    (L718, T697, R951, B709)
   | ['Static40', 'EnabledStatic']
   | child_window(class_name="Static")
    """
    ##############################################################################################################
    """
    Dialog - 'MFC_CCDExample - [CCD Component Version 3.5.7.20]'    (L661, T276, R1260, B764)   
['MFC_CCDExample - [CCD Component Version 3.5.7.20]', 'MFC_CCDExample - [CCD Component Version 3.5.7.20]Dialog', 'Dialog']
child_window(title="MFC_CCDExample - [CCD Component Version 3.5.7.20]", class_name="#32770")   |
   | ComboBox - 'Symphony'    (L676, T325, R802, B345)
   | ['Device SelectionComboBox', 'ComboBox', 'ComboBox0', 'ComboBox1']
   | child_window(title="Symphony", class_name="ComboBox")
   |
   | Button - 'Connect'    (L834, T323, R911, B344)
   | ['Button', 'Connect', 'ConnectButton', 'Button0', 'Button1']
   | child_window(title="Connect", class_name="Button")
   |
   | Button - 'Initialize'    (L927, T325, R1004, B346)
   | ['Initialize', 'Button2', 'InitializeButton']
   | child_window(title="Initialize", class_name="Button")
   |
   | Edit - '10'    (L776, T377, R822, B395)
   | ['Edit', 'Integration Time:Edit', 'Edit0', 'Edit1']
   | child_window(title="10", class_name="Edit")
   |
   | ComboBox - 'IGA Hi Gain'    (L731, T400, R859, B420)
   | ['GainComboBox', 'ComboBox2']
   | child_window(title="IGA Hi Gain", class_name="ComboBox")
   |
   | ComboBox - 'IGA 280 kHz'    (L729, T428, R860, B448)
   | ['ComboBox3', 'ADCComboBox']
   | child_window(title="IGA 280 kHz", class_name="ComboBox")
   |
   | RadioButton - 'Spectra'    (L687, T466, R764, B483)
   | ['SpectraRadioButton', 'RadioButton', 'Spectra', 'RadioButton0', 'RadioButton1']       
   | child_window(title="Spectra", class_name="Button")
   |
   | RadioButton - 'Image'    (L778, T461, R859, B487)
   | ['RadioButton2', 'Image', 'ImageRadioButton']
   | child_window(title="Image", class_name="Button")
   |
   | Edit - '1'    (L955, T382, R1004, B400)
   | ['X StartEdit', 'Edit2']
   | child_window(title="1", class_name="Edit")
   |
   | Edit - '1'    (L955, T404, R1004, B422)
   | ['Y StartEdit', 'Edit3']
   | child_window(title="1", class_name="Edit")
   |
   | Edit - '512'    (L955, T430, R1004, B448)
   | ['X EndEdit', 'Edit4']
   | child_window(title="512", class_name="Edit")
   |
   | Edit - '1'    (L955, T455, R1004, B473)
   | ['Y EndEdit', 'Edit5']
   | child_window(title="1", class_name="Edit")
   |
   | Edit - '1'    (L955, T476, R1004, B494)
   | ['X BinEdit', 'Edit6']
   | child_window(title="1", class_name="Edit")
   |
   | Edit - '1'    (L955, T497, R1004, B515)
   | ['Y BinEdit', 'Edit7']
   | child_window(title="1", class_name="Edit")
   |
   | Button - 'Set Params'    (L685, T493, R757, B514)
   | ['Button3', 'Set Params', 'Set ParamsButton']
   | child_window(title="Set Params", class_name="Button")
   | 
   | Button - 'Start Acq'    (L1151, T521, R1218, B547)
   | ['Start AcqButton', 'Start Acq', 'Button4']
   | child_window(title="Start Acq", class_name="Button")
   |
   | Button - 'Save Data'    (L900, T716, R1000, B746)
   | ['Save Data', 'Button5', 'Save DataButton']
   | child_window(title="Save Data", class_name="Button")
   |
   | Button - 'OK'    (L676, T724, R764, B745)
   | ['OK', 'Button6', 'OKButton']
   | child_window(title="OK", class_name="Button")
   |
   | Button - 'Cancel'    (L778, T724, R866, B745)
   | ['Cancel', 'CancelButton', 'Button7']
   | child_window(title="Cancel", class_name="Button")
   |
   | GroupBox - 'Device Selection'    (L668, T310, R1020, B355)
   | ['Device SelectionGroupBox', 'GroupBox', 'Device Selection', 'GroupBox0', 'GroupBox1'] 
   | child_window(title="Device Selection", class_name="Button")
   |
   | GroupBox - 'Setup'    (L669, T364, R1017, B522)
   | ['GroupBox2', 'Setup', 'SetupGroupBox']
   | child_window(title="Setup", class_name="Button")
   |
   | GroupBox - 'Acquire'    (L1030, T506, R1233, B743)
   | ['GroupBox3', 'Acquire', 'AcquireGroupBox']
   | child_window(title="Acquire", class_name="Button")
   |
   | Static - 'Integration Time:'    (L682, T379, R777, B394)
   | ['Integration Time:Static', 'Static', 'Integration Time:', 'Static0', 'Static1']       
   | child_window(title="Integration Time:", class_name="Static")
   |
   | Static - 'Gain'    (L680, T404, R727, B418)
   | ['Static2', 'Gain', 'GainStatic']
   | child_window(title="Gain", class_name="Static")
   |
   | Static - '<units>'    (L830, T380, R867, B392)
   | ['<units>', 'Static3', '<units>Static']
   | child_window(title="<units>", class_name="Static")
   |
   | GroupBox - 'Info'    (L1030, T313, R1230, B504)
   | ['GroupBox4', 'Info', 'InfoGroupBox']
   | child_window(title="Info", class_name="Button")
   |
   | CheckBox - 'Temp'    (L1042, T331, R1103, B343)
   | ['CheckBox', 'TempCheckBox', 'Temp', 'CheckBox0', 'CheckBox1']
   | child_window(title="Temp", class_name="Button")
   |
   | Static - ''    (L1116, T331, R1170, B346)
   | ['Static4', 'TempStatic']
   | child_window(class_name="Static")
   |
   | Static - 'Chip X:'    (L1044, T380, R1084, B394)
   | ['Chip X:', 'Static5', 'Chip X:Static']
   | child_window(title="Chip X:", class_name="Static")
   |
   | Static - 'Chip Y:'    (L1044, T400, R1091, B414)
   | ['Chip Y:Static', 'Static6', 'Chip Y:']
   | child_window(title="Chip Y:", class_name="Static")
   |
   | Static - '512'    (L1103, T380, R1191, B394)
   | ['512', 'Static7', '512Static']
   | child_window(title="512", class_name="Static")
   |
   | Static - '1'    (L1103, T400, R1171, B417)
   | ['1', 'Static8', '1Static']
   | child_window(title="1", class_name="Static")
   |
   | GroupBox - 'Acq Format'    (L678, T451, R885, B490)
   | ['GroupBox5', 'Acq FormatGroupBox', 'Acq Format']
   | child_window(title="Acq Format", class_name="Button")
   |
   | Static - 'X Start'    (L909, T383, R949, B398)
   | ['X Start', 'Static9', 'X StartStatic']
   | child_window(title="X Start", class_name="Static")
   | 
   | Static - 'Y Start'    (L909, T406, R949, B421)
   | ['Y Start', 'Y StartStatic', 'Static10']
   | child_window(title="Y Start", class_name="Static")
   |
   | Static - 'X End'    (L909, T431, R949, B446)
   | ['X EndStatic', 'Static11', 'X End']
   | child_window(title="X End", class_name="Static")
   |
   | Static - 'Y End'    (L909, T457, R949, B472)
   | ['Y End', 'Static12', 'Y EndStatic']
   | child_window(title="Y End", class_name="Static")
   |
   | Static - 'X Bin'    (L909, T478, R949, B493)
   | ['Static13', 'X Bin', 'X BinStatic']
   | child_window(title="X Bin", class_name="Static")
   |
   | Static - 'Y Bin'    (L909, T499, R949, B514)
   | ['Static14', 'Y BinStatic', 'Y Bin']
   | child_window(title="Y Bin", class_name="Static")
   |
   | Static - 'ADC'    (L682, T431, R728, B446)
   | ['ADC', 'Static15', 'ADCStatic']
   | child_window(title="ADC", class_name="Static")
   |
   | Static - 'Status:'    (L1060, T554, R1106, B566)
   | ['Status:', 'Static16', 'Status:Static', 'Status:Static0', 'Status:Static1']
   | child_window(title="Status:", class_name="Static")
   |
   | Static - 'Update:'    (L1060, T611, R1116, B623)
   | ['Update:', 'Static17', 'Update:Static', 'Update:Static0', 'Update:Static1']
   | child_window(title="Update:", class_name="Static")
   |
   | Static - ''    (L1121, T554, R1219, B601)
   | ['Static18', 'Status:Static2']
   | child_window(class_name="Static")
   |
   | Static - ''    (L1119, T611, R1221, B641)
   | ['Static19', 'Update:Static2']
   | child_window(class_name="Static")
   |
   | Static - 'Firmware Version:'    (L1046, T421, R1167, B433)
   | ['Firmware Version:', 'Static20', 'Firmware Version:Static']
   | child_window(title="Firmware Version:", class_name="Static")
   |
   | Static - 'V3.19 CCD_4000'    (L1046, T437, R1179, B454)
   | ['V3.19 CCD_4000', 'V3.19 CCD_4000Static', 'Static21']
   | child_window(title="V3.19 CCD_4000", class_name="Static")
   |
   | Static - 'Description:'    (L1046, T458, R1158, B472)
   | ['Description:', 'Static22', 'Description:Static']
   | child_window(title="Description:", class_name="Static")
   |
   | Static - 'Jobin Yvon CCD Detector'    (L1046, T475, R1193, B495)
   | ['Jobin Yvon CCD DetectorStatic', 'Static23', 'Jobin Yvon CCD Detector']
   | child_window(title="Jobin Yvon CCD Detector", class_name="Static")
   |
   | Static - 'Name:'    (L1044, T349, R1084, B363)
   | ['Name:', 'Static24', 'Name:Static']
   | child_window(title="Name:", class_name="Static")
   |
   | Static - 'Symphony'    (L1096, T349, R1196, B379)
   | ['Static25', 'SymphonyStatic', 'Symphony']
   | child_window(title="Symphony", class_name="Static")
   |
   | GroupBox - 'Stream Acquisition'    (L676, T529, R1019, B642)
   | ['Stream AcquisitionGroupBox', 'GroupBox6', 'Stream Acquisition']
   | child_window(title="Stream Acquisition", class_name="Button")
   |
   | RadioButton - 'Simple Loop'    (L683, T544, R779, B559)
   | ['RadioButton3', 'Simple LoopRadioButton', 'Simple Loop']
   | child_window(title="Simple Loop", class_name="Button")
   |
   | RadioButton - 'Save to memory'    (L683, T560, R799, B575)
   | ['RadioButton4', 'Save to memoryRadioButton', 'Save to memory']
   | child_window(title="Save to memory", class_name="Button")
   |
   | RadioButton - 'Save to Files'    (L683, T577, R783, B592)
   | ['RadioButton5', 'Save to Files', 'Save to FilesRadioButton']
   | child_window(title="Save to Files", class_name="Button")
   |
   | Button - 'GO'    (L932, T541, R1007, B568)
   | ['Button8', 'GOButton', 'GO']
   | child_window(title="GO", class_name="Button")
   |
   | Static - 'Count:'    (L687, T598, R726, B610)
   | ['Static26', 'Count:', 'Count:Static']
   | child_window(title="Count:", class_name="Static")
   |
   | Static - 'FilePath:'    (L687, T622, R736, B634)
   | ['FilePath:Static', 'Static27', 'FilePath:']
   | child_window(title="FilePath:", class_name="Static")
   |
   | Edit - '1'    (L753, T595, R830, B613)
   | ['Count:Edit', 'Edit8']
   | child_window(title="1", class_name="Edit")
   |
   | Edit - 'c:\temp'    (L753, T617, R1007, B635)
   | ['Edit9', 'FilePath:Edit']
   | child_window(title="c:\temp", class_name="Edit")
   |
   | Static - 'Time (sec):'    (L874, T584, R937, B596)
   | ['Time (sec):', 'Static28', 'Time (sec):Static', 'Time (sec):Static0', 'Time (sec):Static1']
   | child_window(title="Time (sec):", class_name="Static")
   |
   | Static - ''    (L946, T584, R1016, B596)
   | ['Time (sec):Static2', 'Static29']
   | child_window(class_name="Static")
   |
   | Static - 'Iteration:'    (L888, T601, R937, B613)
   | ['Iteration:', 'Static30', 'Iteration:Static', 'Iteration:Static0', 'Iteration:Static1']
   | child_window(title="Iteration:", class_name="Static")
   |
   | Static - ''    (L946, T601, R1016, B613)
   | ['Static31', 'Iteration:Static2']
   | child_window(class_name="Static")
   |
   | Static - 'Min'    (L1061, T656, R1094, B668)
   | ['Min', 'Static32', 'MinStatic', 'MinStatic0', 'MinStatic1']
   | child_window(title="Min", class_name="Static")
   |
   | Static - 'Max'    (L1061, T674, R1094, B686)
   | ['Static33', 'MaxStatic', 'Max', 'MaxStatic0', 'MaxStatic1']
   | child_window(title="Max", class_name="Static")
   |
   | Static - 'Avg'    (L1061, T692, R1094, B704)
   | ['AvgStatic', 'Static34', 'Avg', 'AvgStatic0', 'AvgStatic1']
   | child_window(title="Avg", class_name="Static")
   |
   | Static - 'StdDev'    (L1061, T712, R1112, B724)
   | ['StdDevStatic', 'Static35', 'StdDev', 'StdDevStatic0', 'StdDevStatic1']
   | child_window(title="StdDev", class_name="Static")
   |
   | Static - ''    (L1126, T655, R1228, B669)
   | ['Static36', 'MinStatic2']
   | child_window(class_name="Static")
   |
   | Static - ''    (L1126, T673, R1228, B687)
   | ['Static37', 'MaxStatic2']
   | child_window(class_name="Static")
   |
   | Static - ''    (L1126, T692, R1228, B706)
   | ['AvgStatic2', 'Static38']
   | child_window(class_name="Static")
   |
   | Static - ''    (L1126, T713, R1228, B727)
   | ['StdDevStatic2', 'Static39']
   | child_window(class_name="Static")
   |
   | Button - 'Triggers'    (L827, T655, R925, B678)
   | ['TriggersButton', 'Button9', 'Triggers', 'Triggers0', 'Triggers1']
   | child_window(title="Triggers", class_name="Button")
   |
   | CheckBox - 'Enabled'    (L710, T661, R850, B679)
   | ['CheckBox2', 'Enabled', 'EnabledCheckBox']
   | child_window(title="Enabled", class_name="Button")
   |
   | GroupBox - 'Triggers'    (L673, T643, R1002, B684)
   | ['Triggers2', 'GroupBox7', 'TriggersGroupBox']
   | child_window(title="Triggers", class_name="Button")
   |
   | CheckBox - 'HW Multi Acq'    (L802, T544, R911, B562)
   | ['HW Multi AcqCheckBox', 'CheckBox3', 'HW Multi Acq']
   | child_window(title="HW Multi Acq", class_name="Button")
   |
   | Static - ''    (L718, T697, R951, B709)
   | ['Static40', 'EnabledStatic']
   | child_window(class_name="Static")
    """
    def __init__(self) -> None:
        self.app = Application(backend="win32").start(config.MFCCCDPATH, timeout=10)
        self.app["MFC_CCDExample"].wait(wait_for="enabled",timeout=20)
        time.sleep(3)
        self.app["MFC_CCDExample"]["Connect"].click()
        time.sleep(3)
    
    def Initialize(self) -> None:
        self.app["MFC_CCDExample - [CCD Component Version 3.5.7.20]"]["Initialize"].click()
        time.sleep(12)
    
    def print(self) -> None:
        print(self.app["MFC_CCDExample - [CCD Component Version 3.5.7.20]"].print_control_identifiers())

    def set_exposuretime(self, exposuretime: int | float) -> None:
        self.exposuretime = exposuretime
        self.app["MFC_CCDExample - [CCD Component Version 3.5.7.20]"]["Integration Time:Edit"].set_text(str(self.exposuretime))
        self.app["MFC_CCDExample - [CCD Component Version 3.5.7.20]"]["Set Params"].click()

    def set_config_savetofiles(self, path: str) -> None:
        self.savefolderpath = path
        self.app["MFC_CCDExample - [CCD Component Version 3.5.7.20]"]["Save to Files"].click()
        self.app["MFC_CCDExample - [CCD Component Version 3.5.7.20]"]["FilePath:Edit"].set_text(path)
    
    def start_exposure(self, block: bool = True) -> None:
        """
        args:
            block: bool
                if True, the function will block until the exposure is done.
                if False, the function will return immediately.
        """
        if block and os.path.exists(os.path.join(self.savefolderpath, "IMAGE0001_0001_AREA1_1.txt")):
            os.remove(os.path.join(self.savefolderpath, "IMAGE0001_0001_AREA1_1.txt"))#もしも既にファイルがあれば削除する．（削除しなかったとしても今回の測定で上書きされてしまうから削除しても問題ない）
        self.app["MFC_CCDExample - [CCD Component Version 3.5.7.20]"]["GO"].click()
        if block:
            time.sleep(self.exposuretime + 1)
            while not os.path.exists(os.path.join(self.savefolderpath, "IMAGE0001_0001_AREA1_1.txt")):
                time.sleep(1)


if __name__ == "__main__":
    ihr = ihr320()
    ihr.Initialize()

    path = r"c:\Users\optical group\Documents\individual\kanai"
    sym = Symphony()
    sym.Initialize()
    sym.set_exposuretime(1)
    sym.set_config_savetofiles(path)
    #sym.start_exposure()