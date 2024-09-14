import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My PyQt5 App")
        
        # Set the default window size (width, height)
        self.resize(1000, 800)  # Width: 800, Height: 600
        
        # Alternatively, set the window size and position (x, y, width, height)
        # self.setGeometry(100, 100, 800, 600)  # x: 100, y: 100, Width: 800, Height: 600

        # You can also adjust the window size later if needed
        # self.resize(1024, 768)  # New Size: Width: 1024, Height: 768

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
