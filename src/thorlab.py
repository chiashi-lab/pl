from pylablib.devices import Thorlabs
import config

class motor:
    """
    class to control the Thorlabs stage

    Attributes:
    stage: Thorlabs.KinesisMotor object
    maxlimit: maximum limit of the stage
    minlimit: minimum limit of the stage
    position: current position of the stage

    Methods:
    get_status: get the status of the stage
    get_scale: get the scale of the stage
    get_scale_units: get the scale units of the stage
    get_position: get the position of the stage
    wait_for_stop: wait for the stage to stop
    move_to: move the stage to a position
    move_to_home: move the stage to the home position
    gethome: get the home parameters of the stage
    getparam: get the parameters of the stage
    setparam: set the parameters of the stage
    """
    def __init__(self,home):
        print("connected devices: ", Thorlabs.list_kinesis_devices())
        print(f"trying to connect to device {config.KINESISMOTORID}")
        self.stage = Thorlabs.KinesisMotor(str(config.KINESISMOTORID))
        if home:
            self.move_to_home(block=True)
        self.position = self.get_position()
        self.maxlimit = 1814000
        self.minlimit =  665700
    
    def get_status(self):
        return self.stage.get_status()
    
    def get_scale(self):
        return self.stage.get_scale()
    
    def get_scale_units(self):
        return self.stage.get_scale_units()
    
    def get_position(self):
        return self.stage.get_position()
    
    def wait_for_stop(self):
        self.stage.wait_for_stop()
    
    def move_to(self, position, block):
        if position > self.maxlimit:
            position = self.maxlimit
        elif position < self.minlimit:
            position = self.minlimit
        print(f"stage is moving{position}")
        self.stage.move_to(position)
        if block:
            self.wait_for_stop()
    
    def move_to_home(self,block):
        self.stage.home(sync=block, force=True)

    def gethome(self):
        return self.stage.get_homing_parameters()
    
    def getparam(self, scale=False):
        return self.stage.get_polctl_parameters()
    
    def setparam(self, velocity=None, home_position=None, jog1=None, jog2=None, jog3=None, scale=False):
        self.stage.setup_polctl(velocity=velocity, home_position=home_position, jog1=jog1, jog2=jog2, jog3=jog3, scale=scale)

if __name__ == "__main__":
    stage = motor(home=False)
    stage.move_to(600000,block=True)
    print(stage.get_position())