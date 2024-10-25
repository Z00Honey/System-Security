from PyQt5.QtWidgets import *
from window import MainWindow
import sys

from utils.load import load_stylesheet

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.init_GUI() 
    window.show()
    sys.exit(app.exec_())
