import serial

class shutter:
    def __init__(self, port):
        self.serial = serial.Serial(port=port, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE, rtscts=True, timeout=3)
        self.ch1 = None
        self.ch2 = None

    def send(self, command):
        self.serial.write(command)
        message =  self.serial.readlines()
        if list(message)[0] == 'S':
            return message.lstrip()
        else:
            for _ in range(10):
                message = self.serial.readlines()
                if list(message)[0] == 'S':
                    return message.lstrip()
            return 'Error'

    def getstatus(self, ch):
        message = self.send(b'open?' + str(ch))
        message = message.split(',')
        if ch == 1:
            self.ch1 = message[1]
        else:
            self.ch2 = message[1]

    def open(self, ch):
        self.send(b'open:' + str(ch))
        self.getstatus(ch)
    
    def close(self, ch):
        self.send(b'close:' + str(ch))
        self.getstatus(ch)


if __name__ == '__main__':
    s = shutter('COM5')
    print(s.send('sc'))