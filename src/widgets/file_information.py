from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize
from utils.load import image_base_path

class FileInformation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)       
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.icon_label = QLabel(self)
        icon_path = image_base_path("file_information.png")
        self.icon_label.setPixmap(QPixmap(icon_path).scaled(30, 30)) 
        self.icon_label.setFixedSize(30, 30)

        self.title_label = QLabel("파일 정보", self)

        self.title_layout = QHBoxLayout()
        self.title_layout.addWidget(self.icon_label)
        self.title_layout.addWidget(self.title_label)

        self.layout.addLayout(self.title_layout)

        self.add_horizontal_separator()

        # 밑에 내용 비워두기 (추후에 파일 정보 추가 예정)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def add_horizontal_separator(self):
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.HLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: black; margin-left: 0px; margin-right: 0px;")
        self.layout.addWidget(line_separator)