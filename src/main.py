from superchrome import superchrome
from ophircom import ophircom
from thorlab import motor
import time
from pywinauto.application import Application
import func

def control_power(targetpower,eps=0.001):
    nowpower = ophircom.get_power()
    nowndstep = motor.get_position()

    if nowpower < targetpower - eps:
    elif nowpower > targetpower + eps:
    else:
        print("Already at target power")

if __name__ == "__main__":
    app = Application(backend="win32").start(r"C:\Users\maruk\Desktop\Jobin Yvon\SDK\Examples\C++\FilterWheel\Release\FWExample.exe", timeout=10)
