from pylablib.devices import Thorlabs

class stage:
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
        print("trying to connect to device 27502401")
        self.stage = Thorlabs.KinesisMotor("27502401")
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
    print(Thorlabs.list_kinesis_devices())
    stage = Thorlabs.KinesisMotor("27502401")
    print(stage.get_status())
    stage.move_to(200000)
    stage.wait_for_stop()
    stage.move_to(0)
    stage.wait_for_stop()