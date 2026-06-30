from PyQt6.QtWidgets import QMainWindow, QPushButton, QSlider, QTextEdit, QLabel, QLayout, QErrorMessage, QWidget
from PyQt6.QtCore import QSize, Qt

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ESI-MP2 control GUI")