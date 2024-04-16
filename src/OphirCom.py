# Use of Ophir COM object. 
# Works with python 3.5.1 & 2.7.11
# Uses pywin32
import win32gui
import win32com.client
import time
import traceback

class powermeter:
   """
   class to control the Ophir Power Meter

   Attributes:
   OphirCOM: Ophir COM object
   DeviceList: list of connected devices
   DeviceHandle: handle of the device
   exists: boolean to check if device exists
   ranges: list of ranges
   data: data from the device

   Methods:
   open: open the device
   get_data: get the data from the device
   close: close the device

   """
   def __init__(self):
      self.OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
      self.OphirCOM.StopAllStreams()
      self.OphirCOM.CloseAll()
      self.DeviceList = self.OphirCOM.ScanUSB()
      self.DeviceHandle = None
      self.exists = False
      self.ranges = None
      self.data = None

   def open(self):
      if len(self.DeviceList) > 0:
         self.DeviceHandle = self.OphirCOM.OpenUSBDevice(self.DeviceList[0])
         self.exists = self.OphirCOM.IsSensorExists(self.DeviceHandle, 0)
         if self.exists:
            self.ranges = self.OphirCOM.GetRanges(self.DeviceHandle, 0)
            self.OphirCOM.StartStream(self.DeviceHandle, 0)
         else:
            print('\nNo Sensor attached to {0} for ophir !!!'.format(self.DeviceList[0]))
      else:
         print('\nNo Device attached for ophir !!!')

   def get_data(self):
      self.data = self.OphirCOM.GetData(self.DeviceHandle, 0)
      return self.data

   def close(self):
      self.OphirCOM.StopAllStreams()
      self.OphirCOM.CloseAll()
      self.OphirCOM = None

if __name__ == "__main__":
   try:
      OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
      # Stop & Close all devices
      OphirCOM.StopAllStreams() 
      OphirCOM.CloseAll()
      # Scan for connected Devices
      DeviceList = OphirCOM.ScanUSB()
      print(DeviceList)
      for Device in DeviceList:   	# if any device is connected
         DeviceHandle = OphirCOM.OpenUSBDevice(Device)	# open first device
         exists = OphirCOM.IsSensorExists(DeviceHandle, 0)
         if exists:
            print('\n----------Data for S/N {0} ---------------'.format(Device))

            # An Example for Range control. first get the ranges
            ranges = OphirCOM.GetRanges(DeviceHandle, 0)
            print (ranges)
            # change range at your will
            if ranges[0] > 0:
               newRange = ranges[0]-1
            else:
               newRange = ranges[0]+1
            # set new range
            OphirCOM.SetRange(DeviceHandle, 0, newRange)
            
            # An Example for data retrieving
            OphirCOM.StartStream(DeviceHandle, 0)		# start measuring
            for i in range(60):		
               time.sleep(1)				# wait a little for data
               data = OphirCOM.GetData(DeviceHandle, 0)
               if len(data[0]) > 0:		# if any data available, print the first one from the batch
                  print('Reading = {0}, TimeStamp = {1}, Status = {2} '.format(data[0][0] ,data[1][0] ,data[2][0]))
            
         else:
            print('\nNo Sensor attached to {0} !!!'.format(Device))
   except OSError as err:
      print("OS error: {0}".format(err))
   except:
      traceback.print_exc()

   win32gui.MessageBox(0, 'finished', '', 0)
   # Stop & Close all devices
   OphirCOM.StopAllStreams()
   OphirCOM.CloseAll()
   # Release the object
   OphirCOM = None
