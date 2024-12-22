import serial
import sys
sys.path.append('../')
import config
import time
import warnings

class Focus_adjuster:
    def __init__(self, port: str) -> None:
        self.serial = serial.Serial(port=port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)
        self._position = 0
        self._rpm = 10
        self._steps_per_rotate = config.STEPS_PER_ROTATE_ST42BYH1004
        self._steps_per_sec = self._rpm * self._steps_per_rotate / 60
        time.sleep(5)
        self.move_steps(1, block=True)
        self.set_position(0)

    @property
    def position(self) -> int:
        return self._position

    @property
    def rpm(self) -> int:
        return self._rpm

    def _send_command(self, command: str) -> None:
        """
        Send the command to the autofocus motor
        
        args:
            command: str, command to send to the autofocus motor
        return:
            None
        """
        self.serial.write(command.encode('utf-8'))

    def _read_command(self, split_value: bool = True, max_retry: int = 5) -> str | tuple[str, int]:
        """
        Read the message from the autofocus motor

        args:
            split_value: bool, whether to split the message into command and value
            max_retry: int, number of times to retry reading the message
        return:
            str | tuple[str, int], message from the autofocus motor
            if split_value is True, return tuple of command and value
            else, return the message as string
        """
        for _ in range(max_retry):
            message = self.serial.readline()
            message = message.strip().decode('utf-8')
            if message != '':
                if split_value:
                    message = message.split(' ')
                    return (message[0], int(message[1]))
                return message
            time.sleep(1.0)
        warnings.warn("Failed to read message from the autofocus motor")
        return ''

    def _clear_buffer(self) -> None:
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

    def _clamp(self, value: int, min_bound: int, max_bound: int) -> int:
        return max(min(value, max_bound), min_bound)

    def _check_closeness(self, target: int, current: int, threshold: int) -> bool:
        return abs(target - current) < threshold

    def set_rpm(self, rpm: int, block: bool = True, max_retry: int = 5) -> None:
        """
        Set the rpm of the autofocus motor

        args:
            rpm: int, rpm of the autofocus motor. rpm should be 1 <= rpm <= 80
        return:
            None
        """
        if rpm < 1 or rpm > 80:
            warnings.warn("The rpm should be between 1 and 80")
            rpm = self._clamp(rpm, 1, 80)

        for _ in range(max_retry):
            self._clear_buffer()
            self._send_command("p " + str(rpm) + '\r\n')
            _, res_value = self._read_command(split_value=True)

            # value returned from the motor should be the same as the set value
            if res_value == rpm:
                self._rpm = rpm
                self._steps_per_sec = self._rpm * self._steps_per_rotate / 60
                return


    def move_steps(self, steps: int, block: bool = True, max_retry: int = 5) -> None:
        """
        Move the autofocus motor by the specified number of steps
        command is string. "r |steps|" or "l |steps|"

        args:
            steps: int, number of steps to move the motor. steps should be -1000 <= steps <= 1000
        return:
            None
        """
        if steps < -1000 or steps > 1000:
            warnings.warn("The steps should be between -1000 and 1000")
            steps = self._clamp(steps, -1000, 1000)
        if steps >= 0:
            command = "u " + str(steps) + '\r\n'
        else:
            command = "d " + str(int(-1 * steps)) + '\r\n'

        for _ in range(max_retry):
            self._clear_buffer()
            self._send_command(command)

            if not block:
                self._position += steps
                return

            # if block is true, Wait for the motor to finish moving
            predicted_wait_time = abs(steps) / self._steps_per_sec
            time.sleep(predicted_wait_time)

            _, res_value = self._read_command(split_value=True)
            # value returned from the motor should be the same as the set value
            if self._check_closeness(steps, res_value, 1):
                self._position += res_value
                return

    def set_position(self, position: int) -> None:
        """
        Set the position of the autofocus motor

        args:
            position: int, position to move the autofocus motor
        return:
            None
        """
        self.move_steps(position - self._position, block=True)
        return


if __name__ == '__main__':

    def test():
        obejctive_lens = Focus_adjuster("COM3")
        for i in range(5):
            obejctive_lens.set_rpm(i * 10+ 50)
            print("rpm:",obejctive_lens.rpm)
            obejctive_lens.set_position(0)
            print("pos:",obejctive_lens.position)
            obejctive_lens.set_rpm(30)
            print("rpm:",obejctive_lens.rpm)
            obejctive_lens.set_position(1000)
            print("pos:",obejctive_lens.position)
    
    target = -150
    
    def func(x: int, obejctive_lens: Focus_adjuster) -> int:
        obejctive_lens.set_position(x)
        time.sleep(10)
        return -1 * ((x-target) **2) + 2500

    def test_autofocus():
        obejctive_lens = Focus_adjuster("COM3")
        print("Initialized")
        time.sleep(2)
        obejctive_lens.set_rpm(20)
        obejctive_lens.set_position(target)
        print("now target pos:", obejctive_lens.position)
        time.sleep(2)
        obejctive_lens.set_position(0)
        print("now, Im home")
        time.sleep(2)
        print("start autofocus")
        starttime = time.time()
        
        # 三分探索
        left = -200
        right = 200
        iteration = 0
        while right - left > 9:
            print("iteration:", iteration)
            print("left:", left)
            print("right:", right)
            iteration += 1

            if iteration % 3 == 0:
                obejctive_lens.set_rpm(obejctive_lens._clamp(int((right - left)/7), 2, 20))

            mid1 = left + (right - left) / 3
            mid2 = right - (right - left) / 3
            print("rpm:", obejctive_lens.rpm)
            if func(mid1, obejctive_lens) < func(mid2, obejctive_lens):
                left = mid1
            else:
                right = mid2
        obejctive_lens.set_position(int((left + right) / 2))
        print("result pos:", obejctive_lens.position)
        print("time:", time.time() - starttime)

    test_autofocus()
