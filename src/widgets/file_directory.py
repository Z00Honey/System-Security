from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path

class FileDirectory(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
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
        self.folder_button = self.create_button("folder.png", "폴더")

        self.layout.addWidget(self.desktop_button)
        self.layout.addWidget(self.documents_button)
        self.layout.addWidget(self.downloads_button)
        self.layout.addWidget(self.folder_button)

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
        button.setStyleSheet("text-align: left;")
        button.setFixedSize(180, 40)

        return button
    
    def add_horizontal_separator(self):
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.HLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: rgba(0, 0, 0, 0.5); margin-top: 30px; margin-bottom: 30px; margin-left: 10px; margin-right: 10px; padding: 0;")
        self.layout.addWidget(line_separator)
