import serial
from serial import SerialException
import time

class AutoSerial(serial.Serial):
    def __init__(self, port, baudrate = 9600, connect_timeout = 1, response_timeout = 0.1):
        self.response_timeout = response_timeout
        try:
            super().__init__(port = port, baudrate = baudrate, timeout = self.response_timeout)
            print(f"Connected to {port}")
        except SerialException as e:
            print(f"Failed to connect to port {port}: {e}")
    
    def get_response(self) -> str | None:
        return self.read_until(b"\n").decode("ascii").strip()

    def get_latest_response(self) -> str | None:
        """Return the most recent complete line from the serial buffer."""
        last_line = None
        while True:
            line = self.read_until(b"\n")
            if not line:
                break
            last_line = line.decode("ascii").strip()
            if self.in_waiting == 0:
                break
        return last_line

    def send_command(self, command: str) -> str | None:
        if not command.endswith("\r") or not command.endswith("\n"):
            command += "\r"
        try:
            self.write(command.encode("ascii"))
            time.sleep(self.response_timeout)
            return self.get_response()
        except Exception as e:
            return f"Encountered an error when sending command {command.strip()}: {e}"

class ESI_MP2:
    def __init__(self, serial: AutoSerial):
        self.serial = serial
    def get_status(self):
        return self.serial.send_command("X81")
    def set_motor_speed(self, speed: int  = 1600):
        """
        Set the motor speed to `speed` steps per second
        """
        if speed <= 0 or speed >= 3200:
            print("Speed must be between 0 and 3200 steps/s")
            return None
        return self.serial.send_command(f"X81E{speed}")
    def turn_cw(self):
        return self.serial.send_command("X81C+")
    def turn_ccw(self):
        return self.serial.send_command("X81C-")
    def stop(self):
        return self.serial.send_command("X81!")