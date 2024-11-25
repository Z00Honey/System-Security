from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from utils.load import image_base_path

class FileInformation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)       
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)
        
        self.title_layout = QHBoxLayout()
        
        self.icon_label = QLabel(self)
        icon_path = image_base_path("file_information.png")
        self.icon_label.setPixmap(QPixmap(icon_path).scaled(24, 24))
        
        self.title_label = QLabel("파일 정보", self)
        
        self.title_layout.addWidget(self.icon_label)
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch()
        
        self.layout.addLayout(self.title_layout)
        self.add_horizontal_separator()
        
        self.info_layout = QVBoxLayout()
        self.layout.addLayout(self.info_layout)
        
        self.setFixedHeight(159)
        self.hide()

    def add_horizontal_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line)

    def show_file_info(self, file_info):
        # 기존 정보 클리어
        for i in reversed(range(self.info_layout.count())): 
            self.info_layout.itemAt(i).widget().deleteLater()
            
        # 새 정보 추가
        for key, value in file_info.items():
            info_label = QLabel(f"{key}: {value}")
            self.info_layout.addWidget(info_label)
        
        self.show()  # 정보와 함께 위젯 표시

    def clear_info(self):
        self.hide()