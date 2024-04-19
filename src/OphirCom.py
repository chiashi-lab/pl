# Use of Ophir COM object. 
# Works with python 3.5.1 & 2.7.11
# Uses pywin32
import win32gui
import win32com.client
import time
import traceback

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
      data = self.OphirCOM.GetData(self.DeviceHandle, 0)
      while not data:
         data = self.OphirCOM.GetData(self.DeviceHandle, 0)
      return data
   
   def get_latestdata(self):
      data = self.get_data()
      return data[0][-1]

   def get_range(self):
      self.ranges = self.OphirCOM.GetRanges(self.DeviceHandle, 0)
      return self.ranges
   
   def set_range(self,range):
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
