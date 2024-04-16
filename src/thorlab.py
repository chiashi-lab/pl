from pylablib.devices import Thorlabs
import config

class motor:
    """
    class to control the Thorlabs stage

    Attributes:
    stage: Thorlabs.KinesisMotor object
    maxlimit: maximum limit of the stage
    minlimit: minimum limit of the stage

    Methods:
    get_status: get the status of the stage
    move_to: move the stage to a position
    wait_for_stop: wait for the stage to stop
    """
    def __init__(self):
        print("connected devices: ", Thorlabs.list_kinesis_devices())
        print(f"trying to connect to device {config.KINESISMOTORID}")
        self.stage = Thorlabs.KinesisMotor(str(config.KINESISMOTORID))
        self.maxlimit = 1705825
        self.minlimit =  600000
    
    def get_status(self):
        return self.stage.get_status()
    
    def get_scale(self):
        return self.stage.get_scale()
    
    def get_scale_units(self):
        return self.stage.get_scale_units()
    
    def get_position(self):
        return self.stage.get_position()
    
    def move_to(self, position):
        if position > self.maxlimit:
            position = self.maxlimit
        elif position < self.minlimit:
            position = self.minlimit
        print(f"stage is moving{position}")
        self.stage.move_to(position)
        #not blocked while moving
    
    def wait_for_stop(self):
        self.stage.wait_for_stop()

if __name__ == "__main__":
    stage = motor()
    stage.move_to(600000)
    stage.wait_for_stop()
    print(stage.get_position())