from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent.parent # Parent of parent of this file, should be ../
sys.path.insert(0, str(ROOT)) # Add files from root to path so that we can import from them

from PyQt6.QtWidgets import QMainWindow, QPushButton, QSlider, QTextEdit, QLabel, QApplication, QMessageBox, QHBoxLayout, QVBoxLayout, QWidget, QComboBox, QLayout
from PyQt6.QtCore import Qt, QSize
import time
import serial
from live_graph import LiveGraph
from serial import SerialException

class MainWindow(QMainWindow):
    def __init__(self, perfusion_motor_port: str, pressure_motor_port: str) -> None:
        super().__init__()
        self.setWindowTitle("ESI-MP2 control GUI")
        self.perfusion_motor = ESI_MP2(AutoSerial(perfusion_motor_port))
        self.pressure_motor = ESI_MP2(AutoSerial(pressure_motor_port))
        # GUI setup
        self.setup_widgets()
        self.show()

    def setup_widgets(self):
        main_widget = QWidget(self)

        graphs_widget = QWidget(main_widget)
        controls_widget = QWidget(main_widget)
        controls_widget.setMaximumSize(QSize(500, 300))

        direction_controls = QWidget(controls_widget)
        speed_controls = QWidget(controls_widget)
        speed_buttons = QWidget(speed_controls)
        speed_buttons.setObjectName("speed_buttons")
        speed_buttons.setContentsMargins(0, 0, 0, 0)

        p_control_box = QWidget(controls_widget)
        p_speed_box = QWidget(p_control_box)

        message_box = QMessageBox()

        perfusion_label = QLabel(controls_widget)
        perfusion_label.setText("perfusion Motor")

        stop_movement_button: QPushButton = QPushButton(direction_controls)
        stop_movement_button.setText("Stop Movement")
        def stop():
            message_box.information(None, "Result", self.perfusion_motor.stop(), QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
        stop_movement_button.pressed.connect(stop)

        direction_button: QPushButton = QPushButton(direction_controls)
        direction_button.setCheckable(True)
        direction_button.setText(f"{'CW' if direction_button.isChecked() else 'CCW'}")
        direction_button.toggled.connect(lambda: direction_button.setText(f"{'CW' if direction_button.isChecked() else 'CCW'}"))
        def toggle_direction():
            if direction_button.isChecked():
                self.perfusion_motor.stop()
                response = self.perfusion_motor.turn_ccw()
            else:
                self.perfusion_motor.stop()
                response = self.perfusion_motor.turn_cw()
            message_box.information(None, "Result", response, QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
        direction_button.toggled.connect(toggle_direction)
        
        status_button = QPushButton(direction_controls)
        status_button.setText("Get status")
        def get_status():
            message_box.information(None, "Result", self.perfusion_motor.get_status(), QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
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
        mss_textedit.setFixedSize(QSize(100, 50))
        
        motor_speed_button = QPushButton(speed_buttons)
        motor_speed_button.setText("Set motor speed")
        motor_speed_auto_button = QPushButton(speed_buttons)
        motor_speed_auto_button.setText("Motor speed auto-adjusts")
        motor_speed_auto_button.setCheckable(True)
        
        def update_speed():
            self.perfusion_motor.set_motor_speed(motor_speed_slider.value())
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
        p_movement_options.addItems(['CW', 'Off', 'CCW'])
        p_movement_options.setCurrentIndex(1)
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

        # Graphs
        self.live_graph = LiveGraph(50)
        random_graph = self.live_graph.get_widget(graphs_widget)
        self.live_graph.start_animation(interval=100)

        #Layout
        def layout_children(layout: QLayout, container: QWidget): # doesn't work :(
            for child in container.children():
                if child is QWidget:
                    layout.addWidget(child)
            container.setLayout(layout)
        
        layout = QVBoxLayout(p_speed_box)
        layout.addWidget(p_speed_label, alignment = Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(p_tedit, alignment = Qt.AlignmentFlag.AlignHCenter)
        p_speed_box.setLayout(layout)

        layout = QHBoxLayout(p_control_box)
        layout.addWidget(p_movement_options)
        layout.addWidget(p_slow)
        layout.addWidget(p_speed_box, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(p_speed_up)
        p_control_box.setLayout(layout)

        layout = QHBoxLayout(speed_buttons)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(motor_speed_button)
        layout.addWidget(motor_speed_auto_button)
        speed_buttons.setLayout(layout)

        layout = QVBoxLayout(speed_controls)
        layout.addWidget(speed_buttons)
        layout.addWidget(mss_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(motor_speed_slider)
        layout.addWidget(mss_textedit, alignment=Qt.AlignmentFlag.AlignHCenter)
        speed_controls.setLayout(layout)

        layout = QHBoxLayout(direction_controls)
        layout.addWidget(direction_button)
        layout.addWidget(stop_movement_button)
        layout.addWidget(status_button)
        direction_controls.setLayout(layout)

        layout = QVBoxLayout(controls_widget)
        layout.addWidget(perfusion_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(direction_controls)
        layout.addWidget(speed_controls)
        layout.addWidget(p_header_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(p_control_box)
        controls_widget.setLayout(layout)

        layout = QVBoxLayout(graphs_widget)
        layout.addWidget(random_graph)
        ... # Add more/other graphs later
        graphs_widget.setLayout(layout)

        layout = QHBoxLayout(main_widget)
        layout.addWidget(controls_widget)
        layout.addWidget(graphs_widget)
        main_widget.setLayout(layout)


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

perfusion_motor_port = input("perfusion motor port: ")
pressure_motor_port = input("Pressure motor port: ")
window = MainWindow(perfusion_motor_port, pressure_motor_port)

app.exec()
