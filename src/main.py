from superchrome import superchrome
from ophircom import powermeter
from thorlab import stage
import time



if __name__ == "__main__":
    superchrome = superchrome()
    for i in range(10):
        time.sleep(2)
        superchrome.change_wavelength(300+i*50)