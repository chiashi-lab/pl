from superchrome import superchrome
from ophircom import powermeter
from thorlab import stage
import time



if __name__ == "__main__":
    #superchrome = superchrome()
    powermeter = powermeter()
    powermeter.open(immediate_mode=False)
    stage = stage()
    stage.move_to(600000)
    stage.wait_for_stop()
    print(stage.get_position())
 
