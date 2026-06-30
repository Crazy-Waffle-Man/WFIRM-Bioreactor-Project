from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__() # MUST call
        self.setWindowTitle("App")

        self.label = QLabel()
        self.input = QLineEdit()
        self.input.textChanged.connect(self.label.setText)
        layout = QVBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(self.label)
        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)


app: QApplication = QApplication([]) # Can replace [] with sys.argv


window = MainWindow()
window.show() # MUST call or else window will be hidden

app.exec()