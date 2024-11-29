from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSizePolicy, QMenu,
    QAction, QMessageBox, QProgressDialog
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path
from utils.analysis import analyze_file
from utils.virus_scan import VirusScanThread
from dotenv import load_dotenv
import os


class ToolBar(QWidget):
    """
    파일 작업 및 보안 검사를 위한 버튼들을 포함한 툴바 위젯입니다.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        ToolBar 위젯을 초기화합니다.

        Args:
            parent (QWidget, optional): 부모 위젯입니다. 기본값은 None입니다.
        """
        super().__init__(parent)
        self.parent = parent

        # .env 파일에서 환경 변수를 로드합니다.
        load_dotenv()

        self.setObjectName("tool_bar")
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.create_toolbar_buttons()
        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("tool_bar.css"))

        self.setFixedHeight(40)  # 툴바 높이 설정
        self.setFixedWidth(1000)  # 툴바 너비 설정 (필요에 따라 조정)

    def create_toolbar_buttons(self) -> None:
        """
        툴바 버튼들을 생성하고 레이아웃에 추가합니다.
        """
        button_info = [
            {"name": "new_folder", "icon": "new_folder.png"},
            {"name": "cut", "icon": "cut.png"},
            {"name": "copy", "icon": "copy.png"},
            {"name": "paste", "icon": "paste.png"},
            {"name": "rename", "icon": "rename.png"},
            {"name": "delete", "icon": "delete.png"},
            {"name": "shield", "icon": "shield.png", "menu": True},
        ]

        for info in button_info:
            button = QPushButton()
            button.setIcon(QIcon(image_base_path(info["icon"])))
            button.setIconSize(self.get_icon_size(info["name"]))
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            self.layout.addWidget(button)

            if info["name"] in ["copy", "paste", "cut"]:
                event = getattr(self, f'file_{info["name"]}')
                button.clicked.connect(event)

            if info.get("menu") and info["name"] == "shield":
                menu = self.create_shield_menu()
                button.setMenu(menu)

    def get_icon_size(self, name: str) -> QSize:
        """
        버튼 이름에 따라 적절한 아이콘 크기를 반환합니다.

        Args:
            name (str): 버튼의 이름입니다.

        Returns:
            QSize: 아이콘의 크기입니다.
        """
        if name == "memo":
            return QSize(36, 36)
        elif name == "shield":
            return QSize(32, 32)
        else:
            return QSize(28, 28)

    def create_shield_menu(self) -> QMenu:
        """
        보안 검사를 위한 메뉴를 생성합니다.

        Returns:
            QMenu: 생성된 메뉴입니다.
        """
        menu = QMenu()
        extension_action = QAction("확장자 검사", menu)
        virus_action = QAction("바이러스 검사", menu)

        extension_action.triggered.connect(self.run_extension_check)
        virus_action.triggered.connect(self.run_virus_check)

        menu.addAction(extension_action)
        menu.addAction(virus_action)

        return menu

    def file_copy(self) -> None:
        """복사 작업을 처리합니다."""
        self.parent.file_event('copy')

    def file_cut(self) -> None:
        """잘라내기 작업을 처리합니다."""
        self.parent.file_event('cut')

    def file_paste(self) -> None:
        """붙여넣기 작업을 처리합니다."""
        self.parent.file_event('paste')

    def file_delete(self) -> None:
        """삭제 작업을 처리합니다."""
        self.parent.file_event('delete')

    def run_extension_check(self) -> None:
        """
        선택된 파일에 대해 확장자 검사를 실행합니다.
        """
        main_window = self.window()

        # 현재 선택된 파일 가져오기
        file_list = main_window.file_explorer_bar.file_area.file_list
        current_index = file_list.tree_view.currentIndex()
        if not current_index.isValid():
            self.show_warning_message("경고", "파일을 선택해주세요.")
            return

        file_path = file_list.model.filePath(current_index)

        if file_list.model.isDir(current_index):
            self.show_warning_message("경고", "파일만 검사할 수 있습니다.")
            return

        if self.confirm_action("확장자 검사", "선택한 파일에 대한 포맷 및 확장자 불일치 검사를 진행하시겠습니까?"):
            # 파일 분석 실행
            result = analyze_file(file_path)
            # 검사 결과 표시
            self.show_info_message("확장자 검사 결과", result)

    def run_virus_check(self) -> None:
        """
        선택된 파일 또는 폴더에 대해 바이러스 검사를 실행합니다.
        """
        main_window = self.window()
        file_list = main_window.file_explorer_bar.file_area.file_list
        current_index = file_list.tree_view.currentIndex()

        if not current_index.isValid():
            self.show_warning_message("경고", "파일이나 폴더를 선택해주세요.")
            return

        path = file_list.model.filePath(current_index)

        if file_list.model.isDir(current_index):
            # 폴더 내 파일 확인
            folder_content = os.listdir(path)
            files_only = [f for f in folder_content if os.path.isfile(os.path.join(path, f))]

            if not files_only:
                self.show_info_message("정보", "선택한 폴더에 파일이 없습니다.")
                return

        if self.confirm_action("바이러스 검사", "선택한 파일/폴더에 대한 바이러스 검사를 진행하시겠습니까?"):
            self.start_virus_scan(path)

    def start_virus_scan(self, path: str) -> None:
        """
        바이러스 검사를 시작합니다.

        Args:
            path (str): 검사할 파일 또는 폴더의 경로입니다.
        """
        self.progress_dialog = QProgressDialog("검사 중...", "취소", 0, 100, self)
        self.progress_dialog.setWindowTitle("바이러스 검사")
        self.progress_dialog.setWindowModality(True)

        self.scan_thread = VirusScanThread(path)
        self.scan_thread.finished.connect(self.on_scan_finished)
        self.scan_thread.error.connect(self.on_scan_error)
        self.scan_thread.progress.connect(self.update_progress)

        self.progress_dialog.canceled.connect(self.scan_thread.terminate)
        self.scan_thread.start()
        self.progress_dialog.show()

    def update_progress(self, current: int, total: int) -> None:
        """
        검사 진행 상황을 업데이트합니다.

        Args:
            current (int): 현재 진행 상황입니다.
            total (int): 총 진행 상황입니다.
        """
        if self.progress_dialog:
            progress = int((current / total) * 100)
            self.progress_dialog.setValue(progress)
            self.progress_dialog.setLabelText(f"검사 중... ({current}/{total})")

    def on_scan_finished(self, result: str) -> None:
        """
        바이러스 검사가 완료되었을 때 호출됩니다.

        Args:
            result (str): 검사 결과 메시지입니다.
        """
        self.progress_dialog.close()
        self.show_info_message("검사 완료", result)

    def on_scan_error(self, error_message: str) -> None:
        """
        바이러스 검사 중 오류가 발생했을 때 호출됩니다.

        Args:
            error_message (str): 오류 메시지입니다.
        """
        self.progress_dialog.close()
        self.show_error_message("오류", f"검사 중 오류가 발생했습니다:\n{error_message}")

    def show_warning_message(self, title: str, text: str) -> None:
        """
        경고 메시지 박스를 표시합니다.

        Args:
            title (str): 메시지 박스 제목입니다.
            text (str): 메시지 내용입니다.
        """
        QMessageBox.warning(self, title, text)

    def show_info_message(self, title: str, text: str) -> None:
        """
        정보 메시지 박스를 표시합니다.

        Args:
            title (str): 메시지 박스 제목입니다.
            text (str): 메시지 내용입니다.
        """
        QMessageBox.information(self, title, text)

    def show_error_message(self, title: str, text: str) -> None:
        """
        오류 메시지 박스를 표시합니다.

        Args:
            title (str): 메시지 박스 제목입니다.
            text (str): 메시지 내용입니다.
        """
        QMessageBox.critical(self, title, text)

    def confirm_action(self, title: str, text: str) -> bool:
        """
        사용자에게 작업 확인 대화 상자를 표시합니다.

        Args:
            title (str): 대화 상자 제목입니다.
            text (str): 대화 상자 내용입니다.

        Returns:
            bool: 사용자가 '예'를 선택하면 True를 반환합니다.
        """
        reply = QMessageBox.question(self, title, text, QMessageBox.Yes | QMessageBox.No)
        return reply == QMessageBox.Yes