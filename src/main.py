from pywinauto.application import Application

from pylablib.devices import Thorlabs

import win32gui
import win32com.client
import time

def open_superchrom():
    app = Application(backend="win32").start("C:\Program Files (x86)\Fianium\SuperChrome\SuperChrome.exe", timeout=10)

def init_thorlab():
    print("connected devices: ", Thorlabs.list_kinesis_devices())
    print("trying to connect to device 27502401")
    stage = Thorlabs.KinesisMotor("27502401")
    print("status: ", stage.get_status())
    return stage

def init_ophir():
    ophircom = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
    ophircom.StopAllStreams()
    ophircom.CloseAll()
    device_list = ophircom.ScanUSB()

    assert len(device_list) > 0, "No device found"
    assert len(device_list) == 1, "Multiple devices found"

    device = device_list[0]
    device_handle = ophircom.OpenUSBDevice(device)
    assert ophircom.IsSensorExists(device_handle, 0), "No sensor attached to device"


if __name__ == "__main__":
    stage = init_thorlab()
