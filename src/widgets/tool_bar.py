from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path

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
            {"name": "shield", "icon": "shield.png"},
            {"name": "lock", "icon": "lock.png"},
            {"name": "memo", "icon": "memo.png"},
            {"name": "view_more", "icon": "view_more.png"},
        ]

        for info in button_info:
            button = QPushButton()
            button.setIcon(QIcon(image_base_path(info["icon"])))
            button.setIconSize(QSize(32, 32))
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            self.layout.addWidget(button)
