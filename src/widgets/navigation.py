from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path
from . import global_variable
import os

class NavigationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        # 히스토리 관리
        self.history = []
        self.current_index = -1

        self.back_button = self.create_button("back.png", "뒤로 가기")
        self.forward_button = self.create_button("forward.png", "앞으로 가기")
        self.up_button = self.create_button("up.png", "위로 가기")
        self.refresh_button = self.create_button("refresh.png", "새로 고침")

        # 초기 버튼 상태 설정
        self.back_button.setEnabled(False)
        self.forward_button.setEnabled(False)

        self.layout.addWidget(self.back_button)
        self.layout.addWidget(self.forward_button)
        self.layout.addWidget(self.up_button)
        self.layout.addWidget(self.refresh_button)

        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("address_bar.css"))
        self.setObjectName("navigation_widget")

        # 버튼 이벤트 연결
        self.back_button.clicked.connect(self.go_back)
        self.forward_button.clicked.connect(self.go_forward)
        self.up_button.clicked.connect(self.go_up)
        self.refresh_button.clicked.connect(self.refresh)

        # 초기 경로를 히스토리에 추가
        initial_path = os.path.expanduser("~")
        global_variable.GLOBAL_CURRENT_PATH = initial_path
        self.add_to_history(initial_path)

    def create_button(self, icon_name, tooltip):
        button = QPushButton()
        icon_path = image_base_path(icon_name)
        button.setIcon(QIcon(icon_path))
        button.setToolTip(tooltip)
        
        icon_size = 20
        button_size = 40
        button.setFixedSize(button_size, button_size)
        button.setIconSize(QSize(icon_size, icon_size))
        return button

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

    def update_button_states(self):
        self.back_button.setEnabled(self.current_index > 0)
        self.forward_button.setEnabled(self.current_index < len(self.history) - 1)

    def go_back(self):
        if self.current_index > 0:
            self.current_index -= 1
            path = self.history[self.current_index]
            file_list = self.get_file_list()
            if file_list:
                file_list.set_current_path(path)
            self.update_button_states()

    def go_forward(self):
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            path = self.history[self.current_index]
            file_list = self.get_file_list()
            if file_list:
                file_list.set_current_path(path)
            self.update_button_states()

    def go_up(self):
        file_list = self.get_file_list()
        if file_list:
            current_path = file_list.get_current_path()
            parent_path = os.path.dirname(current_path)
            if os.path.exists(parent_path) and parent_path != current_path:

                global_variable.GLOBAL_CURRENT_PATH = parent_path

                self.add_to_history(parent_path)
                file_list.set_current_path(parent_path)
                self.update_button_states()

    def refresh(self):
        file_list = self.get_file_list()
        if file_list:
            current_path = file_list.get_current_path()
            file_list.set_current_path(current_path)

    def add_to_history(self, path):
        # 현재 위치 이후의 기록 삭제
        self.history = self.history[:self.current_index + 1]
        self.history.append(path)
        self.current_index += 1
        self.update_button_states()
 