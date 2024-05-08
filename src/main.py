from superchrome import superchrome
from ophircom import ophircom
from thorlab import motor
import time
from pywinauto.application import Application
import func

def control_power(targetpower,eps=0.001):
    while (True):
        time.sleep(2)
        nowndstep = motor.get_position()
        ratio = func.step2ratio(nowndstep)
        nowpower = ratio * ophircom.get_power()
        print("Current power: ", nowpower)
        print("Target power: ", targetpower)

        if nowpower < targetpower - eps or targetpower + eps < nowpower:
            byratio = targetpower / nowpower
            byratio = ratio * byratio
            tostep = func.ratio2step(byratio)
            motor.move_to_position(tostep)
        else:
            print("Already at target power")
            break

if __name__ == "__main__":
    app = Application(backend="win32").start(r"C:\Users\maruk\Desktop\Jobin Yvon\SDK\Examples\C++\FilterWheel\Release\FWExample.exe", timeout=10)
