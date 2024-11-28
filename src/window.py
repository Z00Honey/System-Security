from screeninfo import get_monitors
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QFrame
from PyQt5.QtGui import QShowEvent, QRegion, QPainterPath
from PyQt5.QtCore import Qt, QByteArray, QSize, QRectF, QEvent
from widgets.title_bar import WidgetTitleBar
from widgets.address_bar import AddressBar
from widgets.tool_bar import ToolBar
from widgets.file_explorer_bar import FileExplorerBar

from utils.native.util import setWindowNonResizable, isWindowResizable
from utils.load import load_stylesheet
from utils.native.native_event import _nativeEvent

global GLOBAL_CURRENT_PATH

GLOBAL_CURRENT_PATH = ""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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

        self.address_bar = AddressBar(self)  
        self.layout.addWidget(self.address_bar)

        self.add_horizontal_separator()

        self.tool_bar = ToolBar(self)
        self.layout.addWidget(self.tool_bar)
        
        self.add_horizontal_separator()

        self.file_explorer_bar = FileExplorerBar(self)  # FileExplorerBar를 수평 레이아웃에 추가
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

    def show_file_list(self) -> None:
        self.file_explorer_bar.file_area.show_file_list()

    def show_search_results(self) -> None:
        # self.file_explorer_bar.file_area.search_result_list.show()
        self.file_explorer_bar.file_area.show_search_results()

    def get_status_tree_view(self) -> bool:
        search_status = self.file_explorer_bar.file_area.get_status_search_results()
        file_status = self.file_explorer_bar.file_area.get_status_file_list()

        if search_status != file_status:
            if search_status:
                return 1
            elif file_status:
                return 2
        return 0

    def search_result_addItem(self, path) -> None:
        result_items = self.file_explorer_bar.file_area.search_result_list

        result_items.add_item(path)

    def clear_search_result(self):
        self.file_explorer_bar.file_area.search_result_list.clear()

    def file_event(self, mode):
        if mode == 'copy':
            self.file_explorer_bar.file_area.file_list.copySelectedFiles(cut=False)
        elif mode == 'cut':
            self.file_explorer_bar.file_area.file_list.copySelectedFiles(cut=True)
        elif mode == 'paste':
            self.file_explorer_bar.file_area.file_list.pasteFiles()
        elif mode == 'delete':
            self.file_explorer_bar.file_area.file_list.deleteSelectedFiles()
        else:
            return False