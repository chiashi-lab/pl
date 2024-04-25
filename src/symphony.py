from pywinauto.application import Application
import time
import config

class symphony:
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
    def __init__(self):
        self.app = Application(backend="win32").start(config.MFCCCDPATH, timeout=10)
        self.app["MFC_CCDExample"].wait(wait_for="enabled",timeout=20)
        print("Symphony opened")
    
    def print(self):
        self.app["MFC_CCDExample"].print_control_identifiers()


if __name__ == "__main__":
    sym = symphony()
    sym.print()