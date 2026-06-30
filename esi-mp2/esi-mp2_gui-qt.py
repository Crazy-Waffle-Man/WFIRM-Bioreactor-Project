from PyQt6.QtWidgets import QMainWindow, QPushButton, QSlider, QTextEdit, QLabel, QLayout, QMessageBox, QWidget
from PyQt6.QtCore import QSize, Qt
from typing import Callable
import serial, time

class MainWindow(QMainWindow):
    def __init__(self, serial_port: str = "COM17") -> None:
        super().__init__()
        self.setWindowTitle("ESI-MP2 control GUI")
        self.serial = AutoSerial(serial_port)
        self.motor = ESI_MP2(self.serial)
        self.setup_widgets()
        self.show()

    def setup_widgets(self):
        #TODO: Layout
        message_box = QMessageBox()

        stop_movement_button: QPushButton = QPushButton()
        stop_movement_button.setText("Stop Movement")
        def stop():
            message_box.setText(self.motor.stop())
            message_box.show()
        stop_movement_button.pressed.connect(stop)

        direction_button: QPushButton = QPushButton()
        direction_button.setCheckable(True)
        get_direction: Callable = lambda: "ccw" if direction_button.isChecked() else "cw"
        direction_button.setText(f"Currently turning {get_direction()}. Press to toggle.")
        def toggle_direction():
            if get_direction == "ccw":
                self.motor.stop()
                response = self.motor.turn_cw()
            else:
                self.motor.stop()
                response = self.motor.turn_ccw()
            message_box.setText(response)
            message_box.show()
        direction_button.toggled.connect(toggle_direction)
        
        status_button = QPushButton()
        status_button.setText("Get status")
        def get_status():
            message_box.setText(self.motor.get_status())
            message_box.show()
        status_button.pressed.connect(get_status)

        motor_speed_slider = QSlider()
        motor_speed_slider.setRange(1, 3199)
        mss_label = QLabel()
        motor_speed_slider.valueChanged.connect(lambda: mss_label.setText(f"Current speed: {motor_speed_slider.value()}"))
        
        motor_speed_button = QPushButton()
        motor_speed_button.setText("Set motor speed")
        motor_speed_auto_button = QPushButton()
        motor_speed_auto_button.setText("Motor speed auto-adjusts")
        motor_speed_auto_button.setCheckable(True)
        
        def update_speed():
            self.motor.set_motor_speed(motor_speed_slider.value())

        def auto_adjust_speed():
            if motor_speed_auto_button.isChecked(): update_speed()
        motor_speed_slider.valueChanged.connect(auto_adjust_speed)





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