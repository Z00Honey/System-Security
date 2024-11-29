from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path
from ... import global_variable
import os
from utils.secure import SecureFolderManager
from typing import List, Optional


class NavigationWidget(QWidget):
    """
    파일 탐색기를 위한 내비게이션 위젯으로, 뒤로 가기, 앞으로 가기, 위로 가기, 새로 고침 등의 기능을 제공합니다.
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        window: Optional[QWidget] = None,
        secure_manager: Optional[SecureFolderManager] = None
    ) -> None:
        """
        NavigationWidget을 초기화합니다.

        Args:
            parent (QWidget, optional): 부모 위젯입니다.
            window (QWidget, optional): 메인 윈도우 위젯입니다.
            secure_manager (SecureFolderManager, optional): 보안 폴더 매니저 객체입니다.
        """
        super().__init__(parent)
        self.window = window
        self.secure_manager = secure_manager  # 보안 매니저 객체 저장

        # 레이아웃 설정
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        # 히스토리 관리 변수 초기화
        self.history: List[str] = []
        self.current_index: int = -1

        # 내비게이션 버튼 생성
        self.back_button = self.create_button("back.png", "뒤로 가기")
        self.forward_button = self.create_button("forward.png", "앞으로 가기")
        self.up_button = self.create_button("up.png", "위로 가기")
        self.refresh_button = self.create_button("refresh.png", "새로 고침")

        # 초기 버튼 상태 설정
        self.back_button.setEnabled(False)
        self.forward_button.setEnabled(False)

        # 버튼들을 레이아웃에 추가
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

    def create_button(self, icon_name: str, tooltip: str) -> QPushButton:
        """
        아이콘과 툴팁이 있는 버튼을 생성합니다.

        Args:
            icon_name (str): 아이콘 파일 이름입니다.
            tooltip (str): 버튼의 툴팁 텍스트입니다.

        Returns:
            QPushButton: 생성된 버튼 객체입니다.
        """
        button = QPushButton()
        icon_path = image_base_path(icon_name)
        button.setIcon(QIcon(icon_path))
        button.setToolTip(tooltip)

        icon_size = 20
        button_size = 40
        button.setFixedSize(button_size, button_size)
        button.setIconSize(QSize(icon_size, icon_size))
        return button

    def get_main_window(self) -> Optional[QWidget]:
        """
        부모 위젯들을 순회하여 메인 윈도우를 찾습니다.

        Returns:
            QWidget or None: 메인 윈도우 객체를 반환합니다. 찾지 못한 경우 None을 반환합니다.
        """
        parent = self.parent()
        while parent is not None:
            if type(parent).__name__ == 'MainWindow':
                return parent
            parent = parent.parent()
        return None

    def get_file_list(self) -> Optional[QWidget]:
        """
        메인 윈도우에서 파일 리스트 위젯을 가져옵니다.

        Returns:
            QWidget or None: 파일 리스트 위젯을 반환합니다. 찾지 못한 경우 None을 반환합니다.
        """
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'file_explorer_bar'):
            return main_window.file_explorer_bar.file_area.file_list
        return None

    def update_button_states(self) -> None:
        """
        내비게이션 버튼들의 활성화 상태를 업데이트합니다.
        """
        self.back_button.setEnabled(self.current_index > 0)
        self.forward_button.setEnabled(self.current_index < len(self.history) - 1)

    def go_back(self) -> None:
        """
        히스토리에서 이전 경로로 이동합니다.
        """
        if self.current_index > 0:
            self.current_index -= 1
            path = self.history[self.current_index]
            secure_folder_path = (
                os.path.normpath(self.secure_manager.secure_folder_path)
                if self.secure_manager else None
            )

            # 보안 폴더에서 벗어날 때 인증 해제
            if (
                secure_folder_path and
                secure_folder_path not in path and
                self.secure_manager.authenticated
            ):
                self.secure_manager.authenticated = False
                QMessageBox.information(
                    self,
                    "인증 해제",
                    "보안 폴더에서 벗어납니다. 인증이 해제됩니다."
                )

            # 경로 이동 처리
            file_list = self.get_file_list()
            if file_list:
                file_list.set_current_path(path)
            self.update_button_states()

    def go_forward(self) -> None:
        """
        히스토리에서 다음 경로로 이동합니다.
        """
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            path = self.history[self.current_index]
            secure_folder_path = (
                os.path.normpath(self.secure_manager.secure_folder_path)
                if self.secure_manager else None
            )

            # 이동 전에 보안 폴더 접근 시 인증 요구
            if (
                secure_folder_path and
                secure_folder_path in path and
                not self.secure_manager.authenticated
            ):
                self.secure_manager.authenticate()
                if not self.secure_manager.authenticated:
                    self.current_index -= 1  # 원래 위치로 되돌리기
                    return  # 이동 중단

            # 경로 이동 처리
            file_list = self.get_file_list()
            if file_list:
                file_list.set_current_path(path)
            self.update_button_states()

    def go_up(self) -> None:
        """
        현재 디렉토리의 상위 디렉토리로 이동합니다.
        """
        file_list = self.get_file_list()
        if file_list:
            current_path = file_list.get_current_path()
            parent_path = os.path.dirname(current_path)
            secure_folder_path = (
                os.path.normpath(self.secure_manager.secure_folder_path)
                if self.secure_manager else None
            )

            # 보안 폴더를 벗어날 때 인증 해제 및 홈 디렉토리로 이동
            if (
                self.secure_manager and
                self.secure_manager.authenticated and
                secure_folder_path not in parent_path
            ):
                self.secure_manager.authenticated = False
                QMessageBox.information(
                    self,
                    "인증 해제",
                    "보안 폴더에서 벗어납니다. 인증이 해제됩니다."
                )
                parent_path = os.path.expanduser("~")  # 홈 디렉토리로 이동

            # 경로 이동 처리
            if os.path.exists(parent_path) and parent_path != current_path:
                global_variable.GLOBAL_CURRENT_PATH = parent_path
                self.add_to_history(parent_path)
                file_list.set_current_path(parent_path)
                self.update_button_states()

    def refresh(self) -> None:
        """
        현재 뷰를 새로 고침합니다.
        """
        status = self.window.get_status_tree_view()
        print(status)

        if status == 2:  # 파일 리스트가 표시되는 경우
            self.window.show_file_list()
            file_list = self.get_file_list()
            if file_list:
                current_path = file_list.get_current_path()
                file_list.set_current_path(current_path)

    def add_to_history(self, path: str) -> None:
        """
        주어진 경로를 히스토리에 추가합니다.

        Args:
            path (str): 추가할 경로입니다.
        """
        # 현재 위치 이후의 기록 삭제
        self.history = self.history[:self.current_index + 1]
        self.history.append(path)
        self.current_index += 1
        self.update_button_states()