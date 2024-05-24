from superchrome import superchrome
from ophircom import ophircom
from thorlab import Stage, FlipMount
from shutter import shutter
from symphony import Symphony
import time
import func
import numpy as np
import os

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

def pid_control_power(targetpower,wavelength,powermeter, stage, eps=0.001):
    dt = 1
    r = 2.0e5 /targetpower#正規化
    Kp = 1.0 * r
    Ki = 0.01 * r
    Kd = 0.01 * r
    acc = 0
    diff = 0
    prev = 0
    while (True):
        time.sleep(10)
        nowndstep = stage.get_position()
        ratio = func.alnear(wavelength)
        measuredpower = powermeter.get_latestdata()
        nowpower = ratio * measuredpower
        print("measured power: ", measuredpower)
        print("predicted current power: ", nowpower)
        print("now step: ", nowndstep)
        print("\n")

        if nowpower < targetpower - eps or targetpower + eps < nowpower:
            error = nowpower - targetpower
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

def test():
    flipshut = FlipMount()
    flipshut.close()
    shut = shutter('COM5')
    shut.close(2)

    laserchoone = superchrome()

    stage = Stage(home=False)
    stage.move_to(500000, block=True)
    print(f"stage is at {stage.get_position()}")

    shut.open(2)
    flipshut.open()

    powermeter = ophircom()
    powermeter.open()
    powermeter.set_range(4)
    print(f"powermeter is at {powermeter.get_range()}")

    print(f"changing wavelength to 561")
    laserchoone.change_lwbw(wavelength=561, bandwidth=10)
    time.sleep(5)
    print("changed wavelength")
    print(f"powermeter is at {powermeter.get_latestdata()}")
    print("start controlling power")
    time.sleep(5)
    pid_control_power(0.001,561, powermeter, stage, eps=0.0001)
    print("end controlling power")
    time.sleep(2)
    print(f"powermeter is at {powermeter.get_latestdata()}")
    print("waiting for 20s")
    time.sleep(20)

def pl(targetpower, minwavelength, maxwavelength, stepwavelength, integrationtime, path):
    flipshut = FlipMount()
    flipshut.close()
    shut = shutter('COM5')
    shut.close(2)

    laserchoone = superchrome()

    stage = Stage(home=False)
    stage.move_to(500000, block=True)
    print(f"stage is at {stage.get_position()}")

    shut.open(2)
    flipshut.open()

    powermeter = ophircom()
    powermeter.open()
    powermeter.set_range(4)

    symphony = Symphony()
    symphony.Initialize()
    symphony.setintegrationtime(integrationtime)
    symphony.saveconfig(path)

    for wavelength in np.linspace(minwavelength+stepwavelength, maxwavelength, stepwavelength):
        laserchoone.change_lwbw(wavelength=wavelength, bandwidth=stepwavelength)
        #shut.close(2)
        time.sleep(5)
        pid_control_power(targetpower=targetpower, wavelength=wavelength, powermeter=powermeter, stage=stage, eps=targetpower*0.1)
        #shut.open(2)
        symphony.record()
        time.sleep(integrationtime*1.1)
        os.rename(os.path.join(path, "data.txt"), os.path.join(path, f"{wavelength}.txt"))

if __name__ == "__main__":
    test()