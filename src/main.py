from superchrome import superchrome
from ophircom import ophircom
from thorlab import motor
import time



if __name__ == "__main__":
    #superchrome = superchrome()
    powermeter = ophircom()
    powermeter.open(immediate_mode=False)
    stage = motor()
    stage.move_to(600000)
    stage.wait_for_stop()
    print(stage.get_position())
 
