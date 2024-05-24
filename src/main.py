from superchrome import superchrome
from ophircom import ophircom
from thorlab import motor
from shutter import shutter
import time
import func

def control_power(targetpower,powermeter, stage, eps=0.001):
    while (True):
        time.sleep(10)
        nowndstep = stage.get_position()
        ratio = func.mid_targetratio(nowndstep)
        measuredpower = powermeter.get_latestdata()
        nowpower = ratio * measuredpower
        print("measured power: ", measuredpower)
        print("Current power: ", nowpower)
        print("Target power: ", targetpower)
        print("step: ", nowndstep)

        if nowpower < targetpower - eps or targetpower + eps < nowpower:
            print("stage is moving")
            byratio = targetpower / nowpower
            ratio = func.step2ratio(nowndstep)
            tostep = func.ratio2step(byratio*ratio)
            print("byratio: ", byratio)
            print("ratio: ", ratio)
            stage.move_to(tostep)
        else:
            print("Already at target power")
            break

def pid_control_power(targetpower,powermeter, stage, eps=0.001):
    dt = 1
    r = 1e6 * (1/targetpower)#正規化
    Kp = 1 * r
    Ki = 0.1 * r
    Kd = 0.1 * r
    acc = 0
    diff = 0
    prev = 0
    while (True):
        time.sleep(10)
        nowndstep = stage.get_position()
        ratio = func.ratio(nowndstep)
        a = func.a(nowndstep)
        measuredpower = powermeter.get_latestdata()
        nowpower = a * ratio * measuredpower
        print("measured power: ", measuredpower)
        print("predicted current power: ", nowpower)
        print("now step: ", nowndstep)
        print("\n")

        if nowpower < targetpower - eps or targetpower + eps < nowpower:
            error = targetpower - nowpower
            acc += error * dt
            diff = (error - prev) / dt

            tostep = nowndstep + Kp * error + Ki * acc + Kd * diff
            print("move start")
            print("error: ", error)
            print("acc: ", acc)
            print("diff: ", diff)
            print("tostep: ", tostep)
            print("\n")
            stage.move_to(tostep)
            prev = error
        else:
            print("Already at target power")
            break

if __name__ == "__main__":
    shut = shutter()
    shut.close(2)

    laserchoone = superchrome()

    stage = motor(home=True)
    stage.move_to(665700, block=True)
    print(f"stage is at {stage.get_position()}")

    powermeter = ophircom()
    powermeter.open()
    powermeter.set_range(4)
    print(f"powermeter is at {powermeter.get_range()}")

    for i in [561, 633]:
        print(f"changing wavelength to {i}")
        laserchoone.change_lw(wavelength=i, bandwidth=10)
        time.sleep(5)
        print("changed wavelength")
        print(f"powermeter is at {powermeter.get_latestdata()}")
        print("start controlling power")
        control_power(0.001, powermeter, stage, eps=0.0001)
        print("end controlling power")
        time.sleep(2)
        print(f"powermeter is at {powermeter.get_latestdata()}")
        print("waiting for 20s")
        time.sleep(20)