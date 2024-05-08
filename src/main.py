from superchrome import superchrome
from ophircom import ophircom
from thorlab import motor
import time
from pywinauto.application import Application
import func

def control_power(targetpower,powermeter, stage, eps=0.001):
    while (True):
        time.sleep(2)
        nowndstep = stage.get_position()
        ratio = func.step2ratio(nowndstep)
        nowpower = ratio * powermeter.get_power()
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
    laserchoone = superchrome()

    stage = motor(home=True)
    motor.move_to(665700, block=True)
    print(f"stage is at {stage.get_position()}")

    powermeter = ophircom()
    powermeter.open()
    powermeter.set_range(4)
    print(f"powermeter is at {powermeter.get_range()}")

    for i in [550, 650]:
        print(f"changing wavelength to {i}")
        laserchoone.change_lw(wavelength=i)
        time.sleep(5)
        print("changed wavelength")
        print(f"powermeter is at {powermeter.get_data()}")
        print("start controlling power")
        control_power(0.1, powermeter, stage)
        print("end controlling power")
        print(f"powermeter is at {powermeter.get_data()}")