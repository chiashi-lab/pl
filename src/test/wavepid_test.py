import numpy as np
import pandas as pd
import os
import sys
sys.path.append('../')
import config
from measurment import pid_control_wavelength
from driver.zaber import zaber_linear_actuator
from driver.thorlab import thorlabspectrometer
from logger import Logger

class pid_control_wavelength_test:
    def __init__(self, rng) -> None:
        self.rng = rng
        self.positon = self.rng.uniform(config.ZABERMINLIMIT, config.ZABERMAXLIMIT)
        self.time = 0.0

    def get_position(self) -> int:
        self.time += 0.1
        return self.positon


    def get_peak(self) -> float:
        self.time += 0.1
        return -22.684023401501463 * self.positon + 1268.144830916213

    def move_to(self, position: float) -> None:
        if position < config.ZABERMINLIMIT or position > config.ZABERMAXLIMIT:
            position = np.clip(position, config.ZABERMINLIMIT, config.ZABERMAXLIMIT)
        self.time += np.abs(position - self.positon) / 1.0
        self.positon = position
    
    def show_result(self) -> None:
        return self.time
    
    def reset_time(self, time: float) -> None:
        self.time = time
    
    def reset_position(self, position: float) -> None:
        if position:
            self.positon = position
        else:
            self.positon = self.rng.uniform(config.ZABERMINLIMIT, config.ZABERMAXLIMIT)

def sim(Kp, Ki, Kd):
    logger = Logger(None, timestamp_flag=True, log_scroll=None)
    rng = np.random.default_rng()
    mypid_control_wavelength_test = pid_control_wavelength_test(rng)
    wavelist = np.arange(700, 800, 10)
    reslist = []
    for wave in wavelist:
        max_res = 0
        for i in range(100):
            try:
                pid_control_wavelength(wave, mypid_control_wavelength_test, mypid_control_wavelength_test,Kp,Ki,Kd, eps=3, logger=logger)
            except Exception as e:
                print(e)
                return 100
            res = mypid_control_wavelength_test.show_result()
            #print(f"wave:{wave}, res:{res}")
            if res > max_res:
                max_res = res
            mypid_control_wavelength_test.reset_time(0.0)
            mypid_control_wavelength_test.reset_position(None)
        reslist.append(max_res)
    for wave, res in zip(wavelist, reslist):
        print(f"wave:{wave}, res:{res}")
    return np.mean(reslist)

def test():
    tisp = zaber_linear_actuator()
    spectrometer = thorlabspectrometer()
    logger = Logger(None, timestamp_flag=True, log_scroll=None)
    pid_control_wavelength(700, tisp, spectrometer,eps=2, logger=logger)

def get_width(savedir):
    tisp = zaber_linear_actuator()
    spectrometer = thorlabspectrometer()
    logger = Logger(None, timestamp_flag=True, log_scroll=None)
    for wave in range(700, 900 + 5, 5):
        pid_control_wavelength(wave, tisp, spectrometer,eps=2, logger=logger)
        wavelist = spectrometer.wavelengths_corrected
        spectrum = spectrometer.get_spectrum()
        df = pd.DataFrame({"wavelength": wavelist, "spectrum": spectrum})
        df.to_csv(os.path.join(savedir, f"{wave}.csv"), index=False, header=False, sep='\t')


if __name__ == "__main__":
    #print(sim(0.02, 0.02, 0.01))
    get_width(input("savedir:"))