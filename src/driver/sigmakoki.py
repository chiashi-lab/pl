import serial
import time

#シャッターを操作するクラス
#シャッターのコントローラであるssh2cbとシリアル通信を行う

class shutter:
    def __init__(self, port: str) -> None:
        self.serial = serial.Serial(port=port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, rtscts=True, timeout=3)
        time.sleep(1)
        self.getstatus(1)
        time.sleep(1)
        self.getstatus(2)

    def send(self, command: str) -> str: #FIXME. split into _send and _read
        for _ in range(5):
            self.serial.write(command.encode('utf-8'))
            message = self.serial.readline()
            message = message.strip().decode('utf-8')
            if list(message)[0] == 'S':
                return message
            else:
                continue
        return 'Error'

    def getstatus(self, ch: int) -> None:
        message = self.send('open?' + str(ch) + '\r\n')
        message = message.split(',')
        if ch == 1:
            self.ch1 = message[1]
        else:
            self.ch2 = message[1]

    def open(self, ch: int) -> None:
        if (ch == 1 and self.ch1 == 'O') or (ch==2 and self.ch2 == 'O'):
            return
        self.send('open:' + str(ch) + '\r\n')
        if ch ==1:
            self.ch1 ='O'
        else:
            self.ch2='O'
    
    def close(self, ch: int) -> None:
        if (ch == 1 and self.ch1 == 'C') or (ch==2 and self.ch2 == 'C'):
            return
        self.send('close:' + str(ch) + '\r\n')
        if ch ==1:
            self.ch1 ='C'
        else:
            self.ch2='C'


if __name__ == '__main__':
    s = shutter('COM5')
    print("shutter inited")
    print(s.ch1)
    print(s.ch2)
    for i in range(5):
        time.sleep(1)
        s.open(2)
        print("opend")
        print(s.ch1)
        print(s.ch2)
        time.sleep(1)
        s.close(2)
        print("closed")
        print(s.ch1)
        print(s.ch2)