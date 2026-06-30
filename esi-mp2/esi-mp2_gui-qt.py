from PyQt6.QtWidgets import QMainWindow, QPushButton, QSlider, QTextEdit, QLabel, QLayout, QErrorMessage, QWidget
from PyQt6.QtCore import QSize, Qt
import serial, time

class MainWindow(QMainWindow):
    def __init__(self, serial_port: str = "COM17") -> None:
        super().__init__()
        self.setWindowTitle("ESI-MP2 control GUI")
        self.serial = AutoSerial(serial_port)
        self.motor = ESI_MP2(self.serial)
    
    def _setup_cmd_buttons(self):
        stop_movement_button: QPushButton = QPushButton()
        stop_movement_button.setText("Stop Movement")
        stop_movement_button.pressed.connect(self.motor.stop)



class AutoSerial(serial.Serial):
    def __init__(self, port, baudrate = 9600, connect_timeout = 1, response_timeout = 0.1):
        self.response_timeout = response_timeout
        try:
            super.__init__(port, baudrate, connect_timeout)
            print(f"Connected to {port}")
        except serial.SerialException as e:
            print(f"Failed to connect to port {port}: {e}")
    
    def send_command(self, command: str) -> str | None:
        if not command.endswith("\r") or not command.endswith("\n"):
            command += "\r"
        try:
            self.write(command.encode("ascii"))
            time.sleep(self.response_timeout)
            response = self.read(self.in_waiting).decode("ascii").strip()
            return response
        except Exception as e:
            print(f"Encountered an error when sending command {command.strip()}: {e}")
            return None

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
        return self.serial.send_command("X81C!")