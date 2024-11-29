import win32api
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFrame, QLabel,
    QHBoxLayout, QSizePolicy, QMessageBox
)  # 수정: QMessageBox 임포트 추가
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path
from widgets.file.directory import FileDirectory


class Sidebar(QWidget):
    """
    사이드바 위젯으로, 파일 디렉토리, 보안 폴더 접근, 설정 초기화 및 사용자 정보를 표시합니다.
    """

    def __init__(self, parent: QWidget = None, secure_manager: any = None) -> None:
        """
        Sidebar 위젯을 초기화합니다.

        Args:
            parent (QWidget, optional): 부모 위젯입니다. 기본값은 None입니다.
            secure_manager (any, optional): 보안 폴더 관리를 위한 매니저 객체입니다. 기본값은 None입니다.
        """
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setFixedWidth(225)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # 파일 디렉토리 바 추가
        self.file_directory = FileDirectory(self, secure_manager=secure_manager)  # secure_manager 전달
        self.layout.addWidget(self.file_directory)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(spacer)

        self.add_horizontal_separator()

        # 보안 폴더 버튼
        self.security_folder_button = QPushButton("보안 폴더")
        self.add_icon_to_button(self.security_folder_button, "locked-folder.png")
        self.layout.addWidget(self.security_folder_button)

        # 보안 폴더 버튼 클릭 시 go_to_secure_folder 메서드 호출
        self.security_folder_button.clicked.connect(self.go_to_secure_folder)

        self.add_horizontal_separator()

        # 탐색기 설정 버튼
        self.settings_button = QPushButton("초기화")
        self.add_icon_to_button(self.settings_button, "setting.png")
        self.layout.addWidget(self.settings_button)

        # 초기화 버튼 클릭 시, FileDirectory의 reset 메서드 호출
        self.settings_button.clicked.connect(self.on_reset_button_click)

        self.add_horizontal_separator()

        # 로그인된 유저명 가져오기 (win32api 사용)
        user_name = win32api.GetUserName()

        self.user_layout = QHBoxLayout()
        self.user_layout.setContentsMargins(10, 5, 0, 5)
        self.user_layout.setSpacing(5)

        self.login_icon = QLabel(self)
        self.login_icon.setPixmap(QPixmap(image_base_path("login.png")))
        self.login_icon.setFixedSize(40, 40)
        self.user_layout.addWidget(self.login_icon)

        self.user_label = QLabel(f"{user_name}", self)
        self.user_layout.addWidget(self.user_label)
        self.user_layout.addStretch(1)

        self.layout.addLayout(self.user_layout)

        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("sidebar.css"))
        self.setObjectName("sidebar")

    def add_horizontal_separator(self) -> None:
        """
        수평 구분선을 추가합니다.
        """
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.HLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: black; margin: 0; padding: 0;")
        self.layout.addWidget(line_separator)

    def add_icon_to_button(self, button: QPushButton, icon_name: str) -> None:
        """
        버튼에 아이콘을 추가하고 스타일을 설정합니다.

        Args:
            button (QPushButton): 아이콘을 추가할 버튼입니다.
            icon_name (str): 아이콘 파일의 이름입니다.
        """
        icon_path = image_base_path(icon_name)
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(20, 20))
        button.setText(f" {button.text()}")
        button.setFixedHeight(40)

    def go_to_secure_folder(self) -> None:
        """
        보안 폴더로 이동하는 메서드입니다.
        """
        self.file_directory.go_to_secure_folder()

    def on_reset_button_click(self) -> None:
        """
        초기화 버튼 클릭 시 실행되는 메서드로, FileDirectory의 reset 메서드를 호출합니다.
        """
        self.file_directory.reset()