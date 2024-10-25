from screeninfo import get_monitors
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QByteArray
from PyQt5.QtGui import QShowEvent
from widgets.title_bar import TitleBar

from utils.native.util import setWindowNonResizable, isWindowResizable
from utils.load import load_stylesheet
from utils.native.native_event import _nativeEvent

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_GUI()  # Call init_GUI() in the constructor

    def init_GUI(self):
        self.setWindowTitle("FILE Explorer")
        self.setGeometry(*(self.auto_position()))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.init_layout()
        self.qss_load()

    def qss_load(self):
        self.setStyleSheet(load_stylesheet("main.css"))

    def init_layout(self):

        self.title_bar = TitleBar(self)
        self.layout.addWidget(self.title_bar)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addStretch()

    def auto_position(self):

        display = get_monitors()[0]

        width = 1920
        height = 1080
        x = (display.width - width) // 2
        y = (display.height - height) // 2

        return (x, y if y else 100, width, height)

    def setNonResizable(self):
        setWindowNonResizable(self.winId())
        self.title_bar.maximize_button.hide()

    def isResizable(self) -> None:
        return isWindowResizable(self.winId())

    def showEvent(self, event: QShowEvent) -> None:
        self.title_bar.raise_()
        super(MainWindow, self).showEvent(event)

    def nativeEvent(self, event_type: QByteArray, message: int):
        return _nativeEvent(self, event_type, message)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.title_bar.resize(self.width(), self.title_bar.height())