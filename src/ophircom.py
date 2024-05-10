# Use of Ophir COM object. 
# Works with python 3.5.1 & 2.7.11
# Uses pywin32
import win32com.client
import time
import numpy as np

class ophircom:
    """
    class to control the Ophir Power Meter
    if you want to get data, just wait a little before do"get_data"

    Attributes:
    OphirCOM: Ophir COM object
    DeviceList: list of connected devices
    DeviceHandle: handle of the device
    ranges: list of ranges
    immediate_mode: if True, the device will be in immediate mode

    Methods:
    scan: scan the devices
    open: open the device
    get_data: get the data from the device
    get_latestdata: get the latest data from the device
    get_range: get the range of the device
    set_range: set the range of the device
    close: close the device

    """
    def __init__(self):
        """
        only construct the Ophir COM object

        args:
        None

        return:
        None
        """
        self.OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
        self.OphirCOM.StopAllStreams()
        self.OphirCOM.CloseAll()
        self.DeviceList = self.OphirCOM.ScanUSB()
        self.DeviceHandle = None
        self.ranges = None
        self.immediate_mode = False

    def scan(self):
        return self.OphirCOM.ScanUSB()

    def open(self,immediate_mode=False):
        """
        connect to the Ophir Power Meter

        args:
        immediate_mode(bool): if True, the device will be in immediate mode

        return:
        None
        """
        self.immediate_mode = immediate_mode
        if len(self.DeviceList) > 0:
            self.DeviceHandle = self.OphirCOM.OpenUSBDevice(self.DeviceList[0])
            exists = self.OphirCOM.IsSensorExists(self.DeviceHandle, 0)
            if exists:
                self.OphirCOM.ConfigureStreamMode(self.DeviceHandle, 0, 0, 0)
                if self.immediate_mode:
                    self.OphirCOM.ConfigureStreamMode(self.DeviceHandle, 0, 2, 1)
                self.ranges = self.OphirCOM.GetRanges(self.DeviceHandle, 0)
                self.OphirCOM.StartStream(self.DeviceHandle, 0)
            else:
                print('\nNo Sensor attached to {0} for ophir !!!'.format(self.DeviceList[0]))
        else:
            print('\nNo Device attached for ophir !!!')

    def get_data(self):
        """
        get the 2Ddata from the device
        caution: if you want to get the data, just wait a little before do"get_data"
        caution: if you would change the range, data is always 'W' unit

        args:
        None

        return:
        data(3xN float array): 2D(3xN) array of data
        0st row: time
        1st row: power [W]
        2nd row: energy

        if there is no data, return null 2D array(3x0)
        If you want to get the data, just wait a little before do"get_data"
        """
        data = self.OphirCOM.GetData(self.DeviceHandle, 0)
        while not data:
            data = self.OphirCOM.GetData(self.DeviceHandle, 0)
        return data
    
    def get_meandata(self):
        data = self.get_data()
        return np.mean(data[0])
    
    def get_latestdata(self):
        """
        get the latest powerdata from the device
        caution: if you want to get the data, just wait a little before do"get_data"
        caution: if you would change the range, data is always 'W' unit

        args:
        None

        return:
        power(float, [W]): latest powerdata[W]
        """
        data = self.get_data()
        return data[0][-1]

    def get_range(self):
        """
        get the range of the device

        args:
        None

        return:
        ranges(list): list of ranges
        """
        self.ranges = self.OphirCOM.GetRanges(self.DeviceHandle, 0)
        return self.ranges
    
    def set_range(self,range):
        """
        set the range of the device

        close the device and open the device with the range

        args:
        range(int): range to set
            0: AUTO
            1: 3.00W
            2: 300mW
            3: 30mW
            4: 3mW
            5: 300uW
        
        return:
        None
        """
        if not (0<=range and range<=5):
            print("range error!")
            return
        self.OphirCOM.StopAllStreams()

        self.OphirCOM.SetRange(self.DeviceHandle, 0, range)
        self.OphirCOM.ConfigureStreamMode(self.DeviceHandle, 0, 0, 0)
        if self.immediate_mode:
                self.OphirCOM.ConfigureStreamMode(self.DeviceHandle, 0, 2, 1)
        self.ranges = self.OphirCOM.GetRanges(self.DeviceHandle, 0)

        self.OphirCOM.StartStream(self.DeviceHandle, 0)

    def close(self):
        self.OphirCOM.StopAllStreams()
        self.OphirCOM.CloseAll()
        self.OphirCOM = None

if __name__ == "__main__":
    powermeter = ophircom()
    powermeter.open()
    time.sleep(1)
    print(powermeter.get_data())
    print(powermeter.get_range())
    powermeter.set_range(5)
    time.sleep(1)
    print(powermeter.get_data())
    print(powermeter.get_range())
