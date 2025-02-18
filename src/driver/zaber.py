# https://software.zaber.com/motion-library/docs/tutorials/code
# https://software.zaber.com/motion-library/api/py/root/library
# https://www.zaber.com/products/linear-actuators/X-NA/documents
from zaber_motion import Units
from zaber_motion.ascii import Connection
from thorlab import thorlabspectrometer
import sys
sys.path.append("../")
import config


class tisp:
    def __init__(self) -> None:
        self.spectrometer = thorlabspectrometer()
        self.stage_connection = Connection.open_serial_port(config.ZABERPORT)

        print(f"founded {self.stage_connection.detect_devices()} devices")

        self.device = self.stage_connection.detect_devices()[0]

        self.device_axis = self.device.axis(0)
        print("check homing")
        if not self.device_axis.is_homed():
            print("homing")
            self.device_axis.home()
