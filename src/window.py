from screeninfo import get_monitors
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QFrame
from PyQt5.QtGui import QShowEvent, QRegion, QPainterPath
from PyQt5.QtCore import Qt, QByteArray, QSize, QRectF, QEvent
from widgets.titlebar.title_bar import WidgetTitleBar
from widgets.address_bar import AddressBar
from widgets.titlebar.tool_bar import ToolBar
from widgets.file_explorer_bar import FileExplorerBar

from utils.native.util import setWindowNonResizable, isWindowResizable
from utils.load import load_stylesheet
from utils.native.native_event import _nativeEvent
from utils.secure import SecureFolderManager  ##보안폴더

global GLOBAL_CURRENT_PATH

GLOBAL_CURRENT_PATH = ""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.secure_manager = SecureFolderManager() ##보안 객체 생성
        self.init_GUI()

    def init_GUI(self):
        self.setWindowTitle("FILE Explorer")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(*(self.auto_position()))
        self.setObjectName("main")

        self.central_widget = QWidget()
        self.central_widget.setObjectName("central_widget")

        self.setCentralWidget(self.central_widget)

        self.layout : QVBoxLayout = QVBoxLayout(self.central_widget)

        self.init_layout()
        self.qss_load()

    def qss_load(self) -> None:
        self.setStyleSheet(load_stylesheet("main.css")) 

    def init_layout(self) -> None:
        self.title_bar = WidgetTitleBar(self)
        self.layout.addWidget(self.title_bar)

        self.add_horizontal_separator()

        self.address_bar = AddressBar(self, secure_manager=self.secure_manager)  # 수정: 보안 객체 전달
        self.layout.addWidget(self.address_bar)

        self.add_horizontal_separator()

        self.tool_bar = ToolBar(self)
        self.layout.addWidget(self.tool_bar)
        
        self.add_horizontal_separator()

        # 수정: secure_manager를 FileExplorerBar에 전달
        self.file_explorer_bar = FileExplorerBar(self, secure_manager=self.secure_manager)  # FileExplorerBar에 보안 객체 전달
        self.layout.addWidget(self.file_explorer_bar, 1)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

    def auto_position(self) -> tuple:
        display = get_monitors()[0]
        width = 1920
        height = 1080
        x = (display.width - width) // 2
        y = (display.height - height) // 2
        return (x, y if y else 100, width, height)
    
    def add_horizontal_separator(self) -> None:
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.HLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: black;")  
        self.layout.addWidget(line_separator)

    def setNonResizable(self) -> None:
        setWindowNonResizable(self.winId())
        self.title_bar.maximize_button.hide()

    def isResizable(self) -> bool:
        return isWindowResizable(self.winId())

    def showEvent(self, event: QShowEvent) -> None:
        self.title_bar.raise_()
        super(MainWindow, self).showEvent(event)

    def nativeEvent(self, event_type: QByteArray, message: int) -> tuple[int, int]:
        return _nativeEvent(self, event_type, message)

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        self.title_bar.resize(self.width(), self.title_bar.height())
