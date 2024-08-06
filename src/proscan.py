import serial

class PriorStage:
    def __init__(self, port):
        self.serial = serial.Serial(port=port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, rtscts=True, timeout=3)
    
    def send(self, command):
        for _ in range(5):
            self.serial.write(command)
            message = self.serial.readline()
            message = message.strip().decode('utf-8')
            if list(message)[0] == 'S':
                return message
            else:
                continue
        return 'Error'
    
    def go_to(self, xpos, ypos):
        sendm = 'G,' + str(xpos) + ',' + str(ypos) + '\r\n'
        self.send(sendm.encode('utf-8'))