from PyQt5.QtWidgets import *
from window import MainWindow
import sys

sys.dont_write_bytecode = True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())