import serial
import sys
sys.path.append('../')
import config
import time

# 100 steps == 1micrometer
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

    def _clear_buffer(self) -> None:
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

    def get_pos(self, max_retry: int = 5) -> list[int]:
        """
        args: None
        return:
            poslist: list of int
            poslist[0]: X position
            poslist[1]: Y position
            postlist[2]: Z position(Not used)
        """
        self._clear_buffer()
        for _ in range(max_retry):
            self._send_command("P"+ '\r')
            poslist = self._read_command()
            if poslist == '':
                time.sleep(1.0)
                continue
            poslist = poslist.split(',')
            return [int(x) for x in poslist]

    def move_to(self, xpos: int, ypos: int, block: bool = True) -> None:
        """
        args:
            xpos: int
            ypos: int
        return: None
        """
        self._clear_buffer()
        self._send_command('G'+ str(xpos) + ',' + str(ypos) + '\r')
        if block:
            self.block_until_stop()

    def is_moving(self) -> int:
        """
        args: None
        return: 
            3: X and Y are moving
            2: Y is moving
            1: X is moving
            0: X and Y are not moving
        """
        self._clear_buffer()
        self._send_command("$,S"+ '\r')
        res = self._read_command()
        return int(res)

    def block_until_stop(self) -> None:
        while self.is_moving() != 0:
            time.sleep(1)
        return

if __name__ == '__main__':
    stage = Proscan(config.PRIORCOMPORT)
    stage.move_to(10000,900)
    for _ in range(5):
        print(stage.is_moving())
    print(stage.get_pos())