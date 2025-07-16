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
            response = self.serial.readline().strip().decode('utf-8')
            if response:
                return response
            time.sleep(0.1)
        raise TimeoutError("Failed to read response from VGC50X after multiple attempts.")

    def start_measurement(self, interval: int = 1) -> None:
        """
        Start the measurement on the VGC50X.
        """
        self._send_command(f'COM,{interval}')
        response = self._read_response()
        if response != 'OK':
            raise RuntimeError(f"Failed to start measurement: {response}")

if __name__ == "__main__":
    # Example usage
    vgc50x = VGC50X()
    try:
        vgc50x.start_measurement(interval=1)
        for _ in range(5):
            time.sleep(1)
            response = vgc50x._read_response()
            print(f"Response: {response}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        vgc50x.serial.close()