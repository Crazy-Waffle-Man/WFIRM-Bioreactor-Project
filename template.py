from PyQt6.QtWidgets import QApplication, QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__() # MUST call

        self.setWindowTitle("Hello World!")


app: QApplication = QApplication([]) # Can replace [] with sys.argv


window = MainWindow()
window.show() # MUST call or else window will be hidden

app.exec()