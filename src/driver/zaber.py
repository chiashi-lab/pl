# https://software.zaber.com/motion-library/docs/tutorials/code
# https://software.zaber.com/motion-library/api/py/root/library
# https://www.zaber.com/products/linear-actuators/X-NA/documents
from zaber_motion import Units
from zaber_motion.ascii import Connection
import numpy as np
import warnings
import sys
sys.path.append("../")
import config


class zaber_linear_actuator:
    #https://www.zaber.com/manuals/X-NA#m-4-5-initialization
    #ti-spレーザー内での物理的構造上，homeしてしまうとソケットからリニアアクチュエータの軸が外れてしまう
    #全動作後には必ずpark()を呼び出すことでリニアアクチュエータの電源を抜かない限りhomingの必要がない
    #また動作するときにはunpark()する必要があるので注意すること
    def __init__(self) -> None:
        self.stage_connection = Connection.open_serial_port(config.ZABERPORT)

        print(f"founded {self.stage_connection.detect_devices()} devices")

        self._device = self.stage_connection.detect_devices()[0]

        self._device_axis = self._device.get_axis(1)
        self._device_axis.park()
    
    def __del__(self) -> None:
        self._device_axis.park()

    def _home(self) -> None:
        warnings.warn("zaber is homing. Linear actuator will be disconnected from the socket")
        self._device_axis.home()
        self._device_axis.park()
    
    def _check_home(self) -> bool:
        return self._device_axis.is_homed()

    def get_position(self) -> float:
        return self._device_axis.get_position(Units.LENGTH_MILLIMETRES)
    
    def move_to(self, position: float) -> None:
        if self._device_axis.is_parked():
            self._device_axis.unpark()
        if position < config.ZABERMINLIMIT or position > config.ZABERMAXLIMIT:
            warnings.warn(f"zaber {position} is out of range. position is clipped to {position}")
            position = np.clip(position, config.ZABERMINLIMIT, config.ZABERMAXLIMIT)
        self._device_axis.move_absolute(position, Units.LENGTH_MILLIMETRES)
        self._device_axis.park()

if __name__ == "__main__":
    zaber = zaber_linear_actuator()
    position = zaber.get_position()
    print(f"current position is {position}")
    zaber.move_to(position-10)
    position = zaber.get_position()
    print(f"current position is {position}")