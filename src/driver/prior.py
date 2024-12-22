import serial
import sys
sys.path.append('../')
import config
import time

class Proscan:
    def __init__(self, port: str) -> None:
        self.serial = serial.Serial(port=port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_ODD, stopbits=serial.STOPBITS_ONE, timeout=5)

    def send(self, command: str) -> str:
        self.serial.write(command.encode('utf-8'))
        message = self.serial.readline()
        message = message.strip().decode('utf-8')
        return message

    def get_pos(self) -> list[int]:
        """
        args: None
        return:
            poslist: list of int
            poslist[0]: X position
            poslist[1]: Y position
            postlist[2]: Z position(Not used)
        """
        poslist = self.send("P"+ '\r')
        poslist = poslist.split(',')
        poslist = [int(x) for x in poslist]
        return poslist

    def move_to(self, xpos: int, ypos: int) -> None:
        """
        args:
            xpos: int
            ypos: int
        return: None
        """
        self.send('G,' + str(xpos) + ',' + str(ypos) + '\r')

    def is_moving(self) -> int:
        """
        args: None
        return: 
            3: X and Y are moving
            2: Y is moving
            1: X is moving
            0: X and Y are not moving
        """
        res = self.send("$,S"+ '\r')
        return int(res)

    def wait_until_stop(self) -> None:
        while self.is_moving() != 0:
            time.sleep(1)
        return

if __name__ == '__main__':
    stage = Proscan(config.PRIORCOMPORT)
    stage.move_to(10000,900)
    for _ in range(5):
        print(stage.is_moving())
    print(stage.get_pos())