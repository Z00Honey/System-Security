from screeninfo import get_monitors
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QFrame
from PyQt5.QtGui import QShowEvent, QRegion, QPainterPath
from PyQt5.QtCore import Qt, QByteArray, QSize, QRectF, QEvent
from widgets.title_bar import WidgetTitleBar
from widgets.address_bar import AddressBar
from widgets.tool_bar import ToolBar


from utils.native.util import setWindowNonResizable, isWindowResizable
from utils.load import load_stylesheet
from utils.native.native_event import _nativeEvent

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_GUI()

    def init_GUI(self):
        self.setWindowTitle("FILE Explorer")
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(*(self.auto_position()))
        self.setObjectName("main")

        self.central_widget = QWidget()
        self.central_widget.setObjectName("central_widget")

        self.setCentralWidget(self.central_widget)

        self.layout : QVBoxLayout = QVBoxLayout(self.central_widget)
        # self.layout.setAttribute(Qt.WA_TranslucentBackground)

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

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # 파일 시스템 모델 설정
        self.model = QFileSystemModel()
        self.model.setRootPath('')
        self.current_path = self.model.rootPath()

        # 먼저 tabs를 추가
        self.title_bar = WidgetTitleBar(self)
        self.layout.addWidget(self.title_bar)

        # 그 다음 tree view 추가
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.current_path))
        self.tree.setColumnWidth(0, 400) 
        self.tree.setHeaderHidden(False)
        self.tree.setSelectionBehavior(QTreeView.SelectRows)
        self.tree.setEditTriggers(QTreeView.NoEditTriggers)
        self.tree.setRootIsDecorated(False)
        
        self.tree.doubleClicked.connect(self.on_directory_clicked)

        self.layout.addWidget(self.tree)
        self.layout.addStretch()

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

    def on_directory_clicked(self, index):
        # 선택된 경로가 디렉토리인 경우에만 처리
        if self.model.isDir(index):
            # 현재 경로 업데이트
            self.current_path = self.model.filePath(index)
            # 트리뷰의 루트 인덱스를 새로운 디렉토리로 변경
            self.tree.setRootIndex(self.model.index(self.current_path))
