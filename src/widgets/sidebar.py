import win32api
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame, QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path
from widgets.file_directory import FileDirectory

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()

        # 파일 디렉토리 바 추가
        self.file_directory = FileDirectory(self)  # FileDirectory 사용
        self.layout.addWidget(self.file_directory)

        self.add_horizontal_separator()

        # 보안 폴더 버튼
        self.settings_button = QPushButton("보안 폴더")
        self.add_icon_to_button(self.settings_button, "locked-folder.png")  # 아이콘 추가
        self.layout.addWidget(self.settings_button)

        self.add_horizontal_separator()

        # 탐색기 설정 버튼
        self.settings_button = QPushButton("탐색기 설정")
        self.add_icon_to_button(self.settings_button, "setting.png")  # 아이콘 추가
        self.layout.addWidget(self.settings_button)

        self.add_horizontal_separator()

        # 로그인된 유저명 가져오기 (win32api 사용)
        user_name = win32api.GetUserName()

        # 사용자 이름과 로그인 아이콘을 수평으로 배치할 레이아웃 초기화
        self.user_layout = QHBoxLayout()

        # 로그인 아이콘 추가
        self.login_icon = QLabel(self)
        self.login_icon.setPixmap(QPixmap(image_base_path("login.png")))
        self.login_icon.setFixedSize(40, 40)
        self.user_layout.addWidget(self.login_icon)

        # 사용자 이름 레이블 추가
        self.user_label = QLabel(f"{user_name}", self)
        self.user_layout.addWidget(self.user_label)

        # 레이아웃에 사용자 정보 추가
        self.layout.addLayout(self.user_layout)

        # 최종 레이아웃 설정
        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("sidebar.css")) 
        self.setObjectName("sidebar")
        self.setObjectName("file_directory")

    def add_horizontal_separator(self):
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.HLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: black;")
        self.layout.addWidget(line_separator)

    def add_icon_to_button(self, button, icon_name):
        icon_path = image_base_path(icon_name)
        button.setIcon(QIcon(icon_path))  # 버튼에 아이콘 설정
        button.setIconSize(QSize(20, 20))  # 아이콘 크기 설정
        button.setText(f" {button.text()}")  # 아이콘 왼쪽에 텍스트를 배치