from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path
import os

class FileDirectory(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setFixedWidth(225)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        self.home_button = self.create_button("home.png", "홈 디렉토리")
        self.pc_button = self.create_button("pc.png", "내 PC")
        
        self.layout.addWidget(self.home_button)
        self.layout.addWidget(self.pc_button)

        self.add_horizontal_separator()

        self.desktop_button = self.create_button("desktop.png", "바탕화면")
        self.documents_button = self.create_button("documents.png", "문서")
        self.downloads_button = self.create_button("downloads.png", "다운로드")
        #self.folder_button = self.create_button("folder.png", "폴더")

        self.layout.addWidget(self.desktop_button)
        self.layout.addWidget(self.documents_button)
        self.layout.addWidget(self.downloads_button)
        #self.layout.addWidget(self.folder_button)

        # 버튼 클릭 이벤트 연결
        self.home_button.clicked.connect(self.go_to_home)
        self.pc_button.clicked.connect(self.go_to_pc)
        self.desktop_button.clicked.connect(self.go_to_desktop)
        self.documents_button.clicked.connect(self.go_to_documents)
        self.downloads_button.clicked.connect(self.go_to_downloads)
        #self.folder_button.clicked.connect(self.go_to_home)  # 기본적으로 홈 디렉토리로 이동

        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("sidebar.css")) 
        self.setObjectName("file_directory")

    def create_button(self, icon_name, tooltip):
        button = QPushButton()
        icon_path = image_base_path(icon_name)
        button.setIcon(QIcon(icon_path))
        button.setToolTip(tooltip)

        button.setText(tooltip) 
        button.setIconSize(QSize(24, 24))
        button.setStyleSheet("text-align: left; padding-left: 10px;")
        button.setFixedSize(225, 40)

        return button
    
    def add_horizontal_separator(self):
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.HLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: rgba(0, 0, 0, 0.5); margin-top: 30px; margin-bottom: 30px; margin-left: 10px; margin-right: 10px; padding: 0;")
        self.layout.addWidget(line_separator)

    def get_main_window(self):
        parent = self.parent()
        while parent is not None:
            if type(parent).__name__ == 'MainWindow':
                return parent
            parent = parent.parent()
        return None

    def get_file_list(self):
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'file_explorer_bar'):
            return main_window.file_explorer_bar.file_area.file_list
        return None

    def get_navigation_widget(self):
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'address_bar'):
            return main_window.address_bar.navigation_widget
        return None

    def navigate_to(self, path):
        if os.path.exists(path):
            file_list = self.get_file_list()
            nav_widget = self.get_navigation_widget()
            if file_list and nav_widget:
                nav_widget.add_to_history(path)
                file_list.set_current_path(path)

    def go_to_home(self):
        self.navigate_to(os.path.expanduser("~"))

    def go_to_pc(self):
        self.navigate_to("C:\\")

    def go_to_desktop(self):
        self.navigate_to(os.path.expanduser("~\Desktop"))

    def go_to_documents(self):
        self.navigate_to(os.path.expanduser("~\Documents"))

    def go_to_downloads(self):
        self.navigate_to(os.path.expanduser("~\Downloads"))
