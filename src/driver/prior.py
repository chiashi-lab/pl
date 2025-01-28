import serial
import sys
sys.path.append('../')
import config
import time
from decimal import Decimal, ROUND_HALF_UP
import numpy as np

# 100 steps(internal unit) == 1micrometer
class Proscan:
    def __init__(self, port: str) -> None:
        self.serial = serial.Serial(port=port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_ODD, stopbits=serial.STOPBITS_ONE, timeout=5)

    def _send_command(self, command: str) -> None:
        self.serial.write(command.encode('utf-8'))

    def _read_command(self, max_retry: int = 5) -> str:
        for _ in range(max_retry):
            message = self.serial.readline()# realine read until '\n', if timeout, return empty string
            message = message.strip().decode('utf-8')
            if message != '':
                return message
            time.sleep(1.0)

    def get_pos(self, max_retry: int = 5) -> list[int]:
        """
        args: None
        return:
            poslist: list of int
            poslist[0]: X position(internal unit)
            poslist[1]: Y position(internal unit)
            postlist[2]: Z position(Not used)
        """
        for _ in range(max_retry):
            self._send_command("P"+ '\r')
            poslist = self._read_command()
            if poslist == '':
                time.sleep(1.0)
                continue
            poslist = poslist.split(',')
            return [int(x) for x in poslist]

    def get_speed(self) -> float:
        """
        args: None
        return: speed: float (micrometer/sec)
        """
        self._send_command("SMS,u"+ '\r')
        speed = float(self._read_command())
        self._speed = speed
        return speed

    def set_speed(self, speed: float) -> None:
        """
        args: speed: float (micrometer/sec)
        return: None
        """
        speed = Decimal(str(speed)).quantize(Decimal('0.0'), ROUND_HALF_UP)
        self._speed = float(speed)
        self._send_command("SMS,"+ str(speed) + ',u\r')
        return

    def move_to(self, xpos: int, ypos: int, block: bool = True) -> None:
        """
        args:
            xpos: int(internal unit)
            ypos: int(internal unit)
        return: None
        """
        # calculate speed
        now_pos = self.get_pos()
        dist = np.linalg.norm(np.array([xpos, ypos]) - np.array(now_pos[:2]))
        speed = self._dist2speed(dist)
        self.set_speed(speed)

        self._send_command('G,'+ str(xpos) + ',' + str(ypos) + '\r')
        if block:
            self.block_until_stop()
            if speed > 4:
                self.set_speed(4)
                self._send_command('G,'+ str(xpos) + ',' + str(ypos) + '\r')
                self.block_until_stop()

    def _dist2speed(self, dist: float) -> float:
        """
        args: dist: float (internal unit)
        return: speed: float (micrometer/sec)
        """
        if dist < 40 * 100:
            return 4
        elif dist < 1000 * 100:
            return dist * 0.001
        else:
            return 100

    def is_moving(self) -> str:
        """
        args: None
        return: 
            3: X and Y are moving
            2: Y is moving
            1: X is moving
            0: X and Y are not moving
        """
        self._send_command("$,S"+ '\r')
        res = self._read_command()
        return res

    def block_until_stop(self) -> None:
        while self.is_moving() != '0':
            time.sleep(1)
        return

if __name__ == '__main__':
    stage = Proscan(config.PRIORCOMPORT)
    now = time.time()
    stage.move_to(-315200,1402820, True)
    print(stage.get_pos())
    print(time.time()-now)