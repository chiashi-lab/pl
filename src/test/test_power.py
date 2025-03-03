import numpy as np
import pandas as pd
import os
import sys
sys.path.append('../')
import time
from main import pid_control_wavelength
import func
from driver.ophir import juno
from driver.thorlab import ThorlabStage, FlipMount, thorlabspectrometer
from driver.zaber import zaber_linear_actuator
from logger import Logger


def get_wavelength_power_relation(save_path):
    logger = Logger(None, timestamp_flag=True, log_scroll=None)
    flipshut = FlipMount()
    flipshut.open()

    NDfilter = ThorlabStage(home=True)
    NDfilter.move_to(0, block=True)
    logger.log(f"stage is at {NDfilter.get_position()}\n")

    powermeter = juno()
    powermeter.open()
    powermeter.set_range(0)

    tisp = zaber_linear_actuator()
    spectrometer = thorlabspectrometer()

    wavelengthlist = np.arange(700, 900+10, 10)

    measured_power_list = []
    predicted_power_list = []
    for wavelength in wavelengthlist:
        print(f"measuring at {wavelength} nm")
        pid_control_wavelength(wavelength, tisp, spectrometer, logger)
        time.sleep(10)
        measured_power = powermeter.get_latestdata()
        predicted_power = func.ndstep2ratio(0) * measured_power
        print(f"measured power: {measured_power}")
        print(f"predicted power: {predicted_power}")

        measured_power_list.append(measured_power)
        predicted_power_list.append(predicted_power)

    df = pd.DataFrame({
        "wavelength": wavelengthlist,
        "measured_power": measured_power_list,
        "predicted_power": predicted_power_list
    })
    df.to_csv(os.path.join(save_path, "wavelength_power_relation.csv"), index=False)

if __name__ == '__main__':
    get_wavelength_power_relation(input("save_path:"))