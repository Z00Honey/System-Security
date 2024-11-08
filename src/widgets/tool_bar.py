from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path
from ctypes import cdll, c_char_p, create_string_buffer
from utils.analysis import analyze_file


class ToolBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
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
        current_index = main_window.file_list.currentIndex()
        if not current_index.isValid():
            QMessageBox.warning(self, "경고", "파일을 선택해주세요.")
            return

        file_path = main_window.file_list.model.filePath(current_index)
        if main_window.file_list.model.isDir(current_index):
            QMessageBox.warning(self, "경고", "파일만 검사할 수 있습니다.")
            return

        # 파일 분석 실행
        result = analyze_file(file_path)
        
        # 결과 표시
        QMessageBox.information(self, "분석 결과", result)

    def run_virus_check(self):
        print("바이러스 검사 실행")