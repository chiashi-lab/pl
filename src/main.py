from pywinauto.application import Application

from pylablib.devices import Thorlabs

import win32gui
import win32com.client
import time
def wait_until_exits(object, timerstep=1, limit=10):
    timer = 0
    while True:
        time.sleep(timerstep)
        timer += timerstep
        if object.exists():
            break
        assert timer < limit, "too much time is going"

def open_superchrome(timeout=20):
    app = Application(backend="win32").start("C:\Program Files (x86)\Fianium\SuperChrome\SuperChrome.exe", timeout=10)
    app["SuperChrome Initialisation"].wait(wait_for="exists",timeout=timeout)
    app["SuperChrome Initialisation"].OK.click()
    print("SuperChrome opening")
    app["SuperChrome"].wait(wait_for="enabled",timeout=timeout)
    print("SuperChrome opened")
    return app

def change_wavelength(app,wavelength):
    app["SuperChrome"].Edit2.set_text(str(wavelength))
    app["SuperChrome"].Move.click()

def print_superchrome(app):
    app["SuperChrome"].print_control_identifiers()


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
    app = open_superchrome()
    print_superchrome(app)
    for i in range(10):
        time.sleep(2)
        change_wavelength(app, wavelength=300+i*50)
