from PyQt6.QtWidgets import QMainWindow, QPushButton, QSlider, QTextEdit, QLabel, QApplication, QMessageBox, QHBoxLayout, QVBoxLayout, QWidget, QComboBox
from PyQt6.QtCore import Qt, QSize
import time
import serial
from serial import SerialException

class MainWindow(QMainWindow):
    def __init__(self, profusion_motor_port: str, pressure_motor_port: str) -> None:
        super().__init__()
        self.setWindowTitle("ESI-MP2 control GUI")
        self.profusion_motor = ESI_MP2(AutoSerial(profusion_motor_port))
        self.pressure_motor = ESI_MP2(AutoSerial(pressure_motor_port))
        # GUI setup
        self.setup_widgets()
        self.show()

    def setup_widgets(self):
        main_widget = QWidget(self)
        main_widget.setMaximumSize(QSize(500, 300))
        direction_controls = QWidget(main_widget)
        speed_controls = QWidget(main_widget)
        speed_buttons = QWidget(speed_controls)

        message_box = QMessageBox()

        stop_movement_button: QPushButton = QPushButton(direction_controls)
        stop_movement_button.setText("Stop Movement")
        def stop():
            message_box.information(None, "Result", self.profusion_motor.stop(), QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
        stop_movement_button.pressed.connect(stop)

        direction_button: QPushButton = QPushButton(direction_controls)
        direction_button.setCheckable(True)
        direction_button.setText(f"Currently turning {'clockwise' if direction_button.isChecked() else 'counterclockwise'}. Press to toggle.")
        direction_button.toggled.connect(lambda: direction_button.setText(f"Currently turning {'clockwise' if direction_button.isChecked() else 'counterclockwise'}. Press to toggle."))
        def toggle_direction():
            if direction_button.isChecked():
                self.profusion_motor.stop()
                response = self.profusion_motor.turn_ccw()
            else:
                self.profusion_motor.stop()
                response = self.profusion_motor.turn_cw()
            message_box.information(None, "Result", response, QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
        direction_button.toggled.connect(toggle_direction)
        
        status_button = QPushButton(direction_controls)
        status_button.setText("Get status")
        def get_status():
            message_box.information(None, "Result", self.profusion_motor.get_status(), QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
        status_button.pressed.connect(get_status)

        motor_speed_slider = QSlider(speed_controls)
        motor_speed_slider.setRange(1, 3199)
        motor_speed_slider.setOrientation(Qt.Orientation.Horizontal)
        mss_label = QLabel(speed_controls)
        motor_speed_slider.valueChanged.connect(lambda: mss_label.setText(f"Current speed: {motor_speed_slider.value()}"))
        motor_speed_slider.setValue(100)

        mss_textedit = QTextEdit(speed_controls)
        def apply_mss_textedit(text: str):
            result = text.upper().strip()
            result = "".join([char for char in result if char.isdigit()])
            if result != text:
                mss_textedit.setText(result)
                if result.isdigit():
                    if int(result) <= 0 or int(result) >= 3200:
                        return
                    motor_speed_slider.setValue(int(result))
        mss_textedit.textChanged.connect(lambda: apply_mss_textedit(mss_textedit.toPlainText()))
        mss_textedit.setMaximumSize(QSize(100, 30))
        
        motor_speed_button = QPushButton(speed_buttons)
        motor_speed_button.setText("Set motor speed")
        motor_speed_auto_button = QPushButton(speed_buttons)
        motor_speed_auto_button.setText("Motor speed auto-adjusts")
        motor_speed_auto_button.setCheckable(True)
        
        def update_speed():
            self.profusion_motor.set_motor_speed(motor_speed_slider.value())
        motor_speed_button.pressed.connect(update_speed)
        def auto_adjust_speed():
            if motor_speed_auto_button.isChecked(): update_speed()
        motor_speed_slider.valueChanged.connect(auto_adjust_speed)

        # Pressure motor
        p_header_label = QLabel()
        p_header_label.setText("Pressure Motor Controls")

        def p_movement_current_text_changed():
            match p_movement_options.currentText():
                case "CW":
                    self.pressure_motor.turn_cw()
                case "Stop":
                    self.pressure_motor.stop()
                case "CCW":
                    self.pressure_motor.turn_ccw()
        p_movement_options = QComboBox()
        p_movement_options.addItems(['CW', 'Stop', 'CCW'])
        p_movement_options.currentTextChanged.connect(p_movement_current_text_changed)

        p_speed_label = QLabel()
        p_speed_label.setText("Speed: 100")

        def p_update_speed(delta: int):
            p_speed_label.setText("Speed: " + str(int(p_speed_label.text().removeprefix("Speed: ")) + delta))
            self.pressure_motor.set_motor_speed(int(p_speed_label.text().removeprefix("Speed: ")))

        p_slow = QPushButton()
        p_slow.setText("-")
        p_slow.pressed.connect(lambda: p_update_speed(-5))

        p_speed_up = QPushButton()
        p_speed_up.setText("+")
        p_speed_up.pressed.connect(lambda: p_update_speed(5))

        p_tedit = QTextEdit()
        def p_tedit_changed():
            num = int("".join([char for char in p_tedit.toPlainText() if char.isdigit()]))
            if 0 < num or num > 3200:
                return
            p_speed_label.setText("Speed: " + str(num))
            self.pressure_motor.set_motor_speed(int(p_speed_label.text().removeprefix("Speed: ")))
        p_tedit.textChanged.connect(p_tedit_changed)

        #Layout
        
        self.setCentralWidget(main_widget)      

class AutoSerial(serial.Serial):
    def __init__(self, port, baudrate = 9600, connect_timeout = 1, response_timeout = 0.1):
        self.response_timeout = response_timeout
        try:
            super().__init__(port = port, baudrate = baudrate, timeout = connect_timeout)
            print(f"Connected to {port}")
        except SerialException as e:
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

app = QApplication([])

profusion_motor_port = input("Profusion motor port: ")
pressure_motor_port = input("Pressure motor port: ")
window = MainWindow(profusion_motor_port, pressure_motor_port)

app.exec()
