from ctypes import *
import ctypes
import time
dll = windll.LoadLibrary("C:\Program Files (x86)\Fianium\SuperChrome\SuperChromeSDK.dll")

dll.Initialise
dll.RunCalibration  
time.sleep(20)
print(dll.GetCurrentWaveDual("1"))
dll.MoveSyncWaveAndBw(ctypes.c_double(300.0),ctypes.c_double(25.0))
