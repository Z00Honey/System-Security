from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame, QMessageBox  # 수정: QMessageBox 임포트 추가
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path
import os

class FileDirectory(QWidget):
    def __init__(self, parent=None, secure_manager=None):  # 보안 객체 추가
        super().__init__(parent)
        self.secure_manager = secure_manager  # 보안 객체 저장

        self.layout = QVBoxLayout()
        self.setFixedWidth(225)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        # 버튼 생성 및 추가
        self.home_button = self.create_button("home.png", "홈 디렉토리")
        self.pc_button = self.create_button("pc.png", "내 PC")
        self.layout.addWidget(self.home_button)
        self.layout.addWidget(self.pc_button)

        self.add_horizontal_separator()

        self.desktop_button = self.create_button("desktop.png", "바탕화면")
        self.documents_button = self.create_button("documents.png", "문서")
        self.downloads_button = self.create_button("downloads.png", "다운로드")
        self.layout.addWidget(self.desktop_button)
        self.layout.addWidget(self.documents_button)
        self.layout.addWidget(self.downloads_button)

        # 버튼 클릭 이벤트 연결
        self.home_button.clicked.connect(self.go_to_home)
        self.pc_button.clicked.connect(self.go_to_pc)
        self.desktop_button.clicked.connect(self.go_to_desktop)
        self.documents_button.clicked.connect(self.go_to_documents)
        self.downloads_button.clicked.connect(self.go_to_downloads)

        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("sidebar.css"))
        self.setObjectName("file_directory")

    def create_button(self, icon_name, tooltip):
        # 버튼 생성
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
        # 구분선 추가
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.HLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: rgba(0, 0, 0, 0.5); margin: 10px 0;")
        self.layout.addWidget(line_separator)

    def get_main_window(self):
        # MainWindow 객체 가져오기
        parent = self.parent()
        while parent is not None:
            if type(parent).__name__ == 'MainWindow':
                return parent
            parent = parent.parent()
        return None

    def get_file_list(self):
        # 파일 리스트 객체 가져오기
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'file_explorer_bar'):
            return main_window.file_explorer_bar.file_area.file_list
        return None

    def get_navigation_widget(self):
        # 내비게이션 위젯 가져오기
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'address_bar'):
            return main_window.address_bar.navigation_widget
        return None

    def navigate_to(self, path):
        # 보안 폴더 경로 및 현재 경로 확인
        secure_folder_path = os.path.normpath(self.secure_manager.secure_folder_path) if self.secure_manager else None
        current_path = os.path.normpath(path)

        # 보안 폴더 접근 시 인증 요구
        if secure_folder_path and secure_folder_path in current_path and not self.secure_manager.authenticated:
            self.secure_manager.authenticate()
            if not self.secure_manager.authenticated:
                return  # 인증 실패 시 이동 중단

        # 보안 폴더에서 벗어날 경우 인증 해제
        if self.secure_manager and self.secure_manager.authenticated and secure_folder_path not in current_path:
            self.secure_manager.authenticated = False
            QMessageBox.information(self, "인증 해제", "보안 폴더에서 벗어났습니다. 인증이 해제됩니다.")
            path = os.path.expanduser("~")  # 홈 디렉토리로 이동

        # 경로 이동 처리
        file_list = self.get_file_list()
        nav_widget = self.get_navigation_widget()
        if file_list and nav_widget:
            nav_widget.add_to_history(path)
            file_list.set_current_path(path)

    # 버튼별 경로 이동 함수
    def go_to_home(self):
        self.navigate_to(os.path.expanduser("~"))

    def go_to_pc(self):
        self.navigate_to("C:\\")

    def go_to_desktop(self):
        self.navigate_to(os.path.join(os.path.expanduser("~"), "Desktop"))

    def go_to_documents(self):
        self.navigate_to(os.path.join(os.path.expanduser("~"), "Documents"))

    def go_to_downloads(self):
        self.navigate_to(os.path.join(os.path.expanduser("~"), "Downloads"))

    # 추가된 보안 폴더로 이동하는 메서드
    def go_to_secure_folder(self):
        self.navigate_to(self.secure_manager.secure_folder_path)

    # === 추가된 부분 ===
    # 초기화 메서드 (비밀번호 초기화)
    def reset(self):
        if self.secure_manager.authenticated:  # 보안 폴더에 접근한 경우에만 초기화 처리
            self.secure_manager.pwd_mgr.reset()  # 비밀번호 관리 초기화
            # QMessageBox.information(self, "초기화 완료", "비밀번호가 초기화되었습니다.")  # 수정: 초기화 완료 메시지 제거
        else:
            # 보안 폴더에 접근하지 않은 경우, 경고 메시지
            QMessageBox.warning(self, "보안 폴더 접근", "먼저 보안 폴더에 접근해 주세요.")
            self.go_to_secure_folder()  # 보안 폴더로 이동
    # === 추가된 부분 끝 ===
