import serial
import time
import sys
sys.path.append('../')
import config

class VGC50X:
    """
    Class to control the VGC50X via serial communication.

    Attributes:
    port: Serial port object

    """

    def __init__(self, port: str = config.VGC50X_PORT) -> None:
        """
        Initialize the VGC50X controller.

        Args:
            port: Serial port to connect to the VGC50X.
        """
        self.serial = serial.Serial(port=port, baudrate=115200, bytesize=serial.EIGHTBITS,
                                    parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)

    def _send_command(self, command: str) -> None:
        """
        Send a command to the VGC50X.

        Args:
            command: Command string to send.
        """
        self.serial.write((command + '\r\n').encode('utf-8'))

    def _read_response(self, max_retry: int = 5) -> str:
        """
        Read the response from the VGC50X.

        Args:
            max_retry: Number of retries to read the response.
        
        Returns:
            Response string from the VGC50X.
        """
        for _ in range(max_retry):
            response = self.serial.readlines()
            if response:
                response = [line.decode('utf-8').strip() for line in response if line]
                return response
            time.sleep(0.1)
        raise TimeoutError("Failed to read response from VGC50X after multiple attempts.")

    def start_measurement(self, interval: int = 1) -> None:
        """
        Start the measurement on the VGC50X.
        args:
            interval: Measurement interval.
                0 : 100 ms
                1 : 1 s
                2 : 1 min
        """
        assert interval in [0, 1, 2], "Interval must be 0, 1, or 2."
        self._send_command(f'COM,{interval}')

    def get_pressure(self) -> float:
        """
        Get the latest pressure reading from the VGC50X.

        Returns:
            Latest pressure reading as a float.
        """
        try:
            response = self._read_response()
            latest_response = response[-1] if response else ''
            pressure = float(latest_response.split(',')[1])
            return pressure
        except Exception as e:
            print(f"Error parsing pressure response: {e}")
            return 0.0

if __name__ == "__main__":
    def test():
        # Example usage
        vgc50x = VGC50X()
        vgc50x.start_measurement(interval=1)
        for i in range(5):
            print(f"Pressure reading {i+1}: {vgc50x.get_pressure()} Pa")

    test()