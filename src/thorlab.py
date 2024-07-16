from pylablib.devices import Thorlabs
import config
#thorlabsのデバイスを操作するクラス定義
#pylablibというライブラリを使っている
#StageクラスはThorlabs.KinesisMotorを使ってNDフィルターが設置されているステージを操作する
#FlipMountクラスはThorlabs.MFFを使ってターミネーターへのミラーが設置されているフリップマウントを操作する

class Stage:
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
        """
        connect to the Thorlabs stage

        args:
        home: if True, the stage will be moved to the home position

        return:
        None
        """
        print("connected kinesis devices: ", Thorlabs.list_kinesis_devices())
        print(f"trying to connect to kinesis device {config.KINESISSTAGEMOTORID}")
        self.stage = Thorlabs.KinesisMotor(str(config.KINESISSTAGEMOTORID))
        if home:
            self.move_to_home(block=True)
        self.position = self.get_position()
        self.maxlimit = config.KINESISSTAGEMAXLIMIT
        self.minlimit =  config.KINESISSTAGEMINLIMIT
    
    def get_status(self):
        return self.stage.get_status()
    
    def get_scale(self):
        return self.stage.get_scale()
    
    def get_scale_units(self):
        return self.stage.get_scale_units()
    
    def get_position(self):
        """
        get the position of the stage

        args:
        None

        return:
        position(int): current position of the stage
        """
        return self.stage.get_position()
    
    def wait_for_stop(self):
        """
        wait for the stage to stop

        args:
        None

        return:
        None
        """
        self.stage.wait_for_stop()
    
    def move_to(self, position, block=True):
        """
        move the stage to a position
        
        args:
        position(int): position to move
        block(bool): if True, the function will wait for the stage to stop
        """
        if position > self.maxlimit:
            position = self.maxlimit
        elif position < self.minlimit:
            position = self.minlimit
        print(f"stage is moving to {position}")
        self.stage.move_to(position)
        if block:
            self.wait_for_stop()
    
    def move_to_home(self,block):
        """
        move the stage to the home position

        args:
        block(bool): if True, the function will wait for the stage to stop

        return:
        None
        """
        print("stage is homing")
        self.stage.home(sync=block, force=True)
        print("homing done")

    def gethome(self):
        return self.stage.get_homing_parameters()
    
    def getparam(self, scale=False):
        return self.stage.get_polctl_parameters()
    
    def setparam(self, velocity=None, home_position=None, jog1=None, jog2=None, jog3=None, scale=False):
        self.stage.setup_polctl(velocity=velocity, home_position=home_position, jog1=jog1, jog2=jog2, jog3=jog3, scale=scale)

class FlipMount:
    def __init__(self):
        self.flip = Thorlabs.MFF(str(config.KINESISMFFID))
        self.state = self.flip.get_state()
    
    def open(self):
        self.flip.move_to_state(1)
        self.state = self.flip.get_state()

    def close(self):
        self.flip.move_to_state(0)
        self.state = self.flip.get_state()

if __name__ == "__main__":
    Thorlabs.list_kinesis_devices()
    
    stage = Stage(home=False)
    stage.move_to(1400000,block=True)
    print(f"moved{stage.get_position()}")

    flip = FlipMount()
    print(flip.state)