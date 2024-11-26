from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSizePolicy, QMenu,
    QAction, QMessageBox, QProgressDialog
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path
from utils.analysis import analyze_file
from utils.virus_scan import VirusScanThread
from dotenv import load_dotenv
import os


class ToolBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load environment variables from .env file
        load_dotenv()

        self.setObjectName("tool_bar")
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.create_toolbar_buttons()
        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("tool_bar.css"))

        self.setFixedHeight(40)  # 툴바 높이 설정
        self.setFixedWidth(1000)  # 툴바 너비 설정 (예시, 필요에 따라 조정)

    def create_toolbar_buttons(self):
        button_info = [
            {"name": "new_folder", "icon": "new_folder.png"},
            {"name": "cut", "icon": "cut.png"},
            {"name": "copy", "icon": "copy.png"},
            {"name": "paste", "icon": "paste.png"},
            {"name": "rename", "icon": "rename.png"},
            {"name": "share", "icon": "share.png"},
            {"name": "delete", "icon": "delete.png"},
            {"name": "shield", "icon": "shield.png", "menu": True},
            {"name": "lock", "icon": "lock.png"},
            {"name": "memo", "icon": "memo.png"},
            {"name": "view_more", "icon": "view_more.png"},
        ]

        for info in button_info:
            button = QPushButton()
            button.setIcon(QIcon(image_base_path(info["icon"])))
            button.setIconSize(QSize(32, 32))
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

            if info.get("menu") and info["name"] == "shield":
                menu = QMenu(button)

                extension_action = QAction("확장자 검사", menu)
                virus_action = QAction("바이러스 검사", menu)

                extension_action.triggered.connect(self.run_extension_check)
                virus_action.triggered.connect(self.run_virus_check)

                menu.addAction(extension_action)
                menu.addAction(virus_action)

                button.setMenu(menu)

            self.layout.addWidget(button)

    def run_extension_check(self):
        # MainWindow 인스턴스 찾기
        main_window = self.window()

        # 현재 선택된 파일 가져오기
        current_index = main_window.file_explorer_bar.file_area.file_list.tree_view.currentIndex()
        if not current_index.isValid():
            QMessageBox.warning(self, "경고", "파일을 선택해주세요.")
            return

        file_path = main_window.file_explorer_bar.file_area.file_list.model.filePath(current_index)
        if main_window.file_explorer_bar.file_area.file_list.model.isDir(current_index):
            QMessageBox.warning(self, "경고", "파일만 검사할 수 있습니다.")
            return

        # 확인 메시지 표시
        reply = QMessageBox.question(
            self,
            '확장자 검사',
            f'선택한 파일을 검사하시겠습니까?\n\n파일: {file_path}',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 파일 분석 실행
            result = analyze_file(file_path)
            QMessageBox.information(self, "분석 결과", result)

    def run_virus_check(self):
        main_window = self.window()
        current_index = main_window.file_explorer_bar.file_area.file_list.tree_view.currentIndex()
        
        if not current_index.isValid():
            QMessageBox.warning(self, "경고", "파일이나 폴더를 선택해주세요.")
            return

        path = main_window.file_explorer_bar.file_area.file_list.model.filePath(current_index)

        reply = QMessageBox.question(
            self,
            "바이러스토탈을 이용한 평판 검사",
            "선택한 파일/폴더에 대한 바이러스토탈 평판 검사를 진행하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.progress_dialog = QProgressDialog("검사 중...", "취소", 0, 100, self)
            self.progress_dialog.setWindowTitle("바이러스토탈을 이용한 평판 검사")
            self.progress_dialog.setWindowModality(True)
            
            self.scan_thread = VirusScanThread(path)
            self.scan_thread.finished.connect(self.on_scan_finished)
            self.scan_thread.error.connect(self.on_scan_error)
            self.scan_thread.progress.connect(self.update_progress)
            
            self.progress_dialog.canceled.connect(self.scan_thread.terminate)
            self.scan_thread.start()
            self.progress_dialog.show()

    def update_progress(self, current, total):
        if self.progress_dialog:
            progress = int((current / total) * 100)
            self.progress_dialog.setValue(progress)
            self.progress_dialog.setLabelText(f"검사 중... ({current}/{total})")

    def on_scan_finished(self, result):
        self.progress_dialog.close()
        QMessageBox.information(self, "검사 완료", result)

    def on_scan_error(self, error_message):
        self.progress_dialog.close()
        QMessageBox.critical(self, "오류", f"검사 중 오류가 발생했습니다:\n{error_message}")
