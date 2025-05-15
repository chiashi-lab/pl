import os
import sys
import time
sys.path.append('../')
from driver.horiba import Symphony
from driver.thorlab import FlipMount

def test_symphony(savedir):
    flipshut = FlipMount()
    flipshut.close()
    print("flipshut is closed")

    symphony = Symphony()
    symphony.Initialize()
    for exposure_time in [10, 30, 60, 120, 180, 300]:
        print(f"exposure time: {exposure_time}")
        savedir_exposure = os.path.join(savedir, str(exposure_time))
        if not os.path.exists(savedir_exposure):
            os.makedirs(savedir_exposure)
        symphony.set_exposuretime(exposure_time)
        symphony.set_config_savetofiles(savedir_exposure)
        time.sleep(5)
        print(f"length{36000 / exposure_time}")
        for i in range(3600 / exposure_time):
            print(f"exposure {i}")
            symphony.start_exposure(block=True)
            os.rename(os.path.join(savedir_exposure, "IMAGE0001_0001_AREA1_1.txt"), os.path.join(savedir_exposure, f"{i}.txt"))
    

if __name__ == '__main__':
    savedir = input("save_dir:").strip('"')
    test_symphony(savedir)