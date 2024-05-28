from superchrome import superchrome
from ophircom import ophircom
from thorlab import Stage, FlipMount
from shutter import shutter
from symphony import Symphony
from ihr320 import ihr320
import time
import func
import numpy as np
import os


def pid_control_power(targetpower,wavelength,powermeter, stage, eps=0.001):
    dt = 1
    r = 2.0e5 /targetpower#正規化
    Kp = 1.0 * r
    Ki = 0.05 * r
    Kd = 0.05 * r
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

def pl(targetpower, minwavelength, maxwavelength, stepwavelength, integrationtime, centerwavelength, grating, slit, path):
    if not os.path.exists(path):
        os.makedirs(path)

    flipshut = FlipMount()
    flipshut.close()
    shut = shutter('COM5')
    shut.close(2)

    grate = ihr320()
    grate.Initialize()

    laserchoone = superchrome()

    grate.setallconfig(centerwavelength=centerwavelength, grating=grating, frontslit=slit, sideslit=0)

    stage = Stage(home=True)
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

    for wavelength in np.arange(minwavelength, maxwavelength+stepwavelength, stepwavelength):
        laserchoone.change_lwbw(wavelength=wavelength, bandwidth=stepwavelength)
        #shut.close(2)
        time.sleep(5)
        pid_control_power(targetpower=targetpower, wavelength=wavelength, powermeter=powermeter, stage=stage, eps=targetpower*0.05)
        #shut.open(2)
        symphony.record()
        time.sleep(integrationtime*1.1)
        os.rename(os.path.join(path, "IMAGE0001_0001_AREA1_1.txt"), os.path.join(path, f"{wavelength}.txt"))
    
    shut.close(2)
    flipshut.close()

if __name__ == "__main__":
    path = r"c:\Users\optical group\Documents\individual\kanai"
    pl(targetpower=0.002, minwavelength=500, maxwavelength=800, stepwavelength=10, integrationtime=120, path=path)