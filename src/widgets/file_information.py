from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from collections import defaultdict
from utils.load import image_base_path, load_stylesheet
import os

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
        self.setStyleSheet(load_stylesheet("file_information.css")) 
        self.setObjectName("file_information")
        
        self.setFixedHeight(180)
        self.hide()

    def add_horizontal_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line)

    def get_folder_contents_count(self, folder_path):
        try:
            items = os.listdir(folder_path)
            file_count = len([item for item in items if os.path.isfile(os.path.join(folder_path, item))])
            folder_count = len([item for item in items if os.path.isdir(os.path.join(folder_path, item))])
            return file_count, folder_count
        except:
            return 0, 0

    def get_file_types(self, folder_path):
        try:
            items = os.listdir(folder_path)
            file_types = defaultdict(int)
            
            for item in items:
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    _, ext = os.path.splitext(item)
                    if ext:
                        file_types[ext.upper()] += 1
            return dict(file_types)
        except:
            return {}

    def show_file_info(self, file_info):
        for i in reversed(range(self.info_layout.count())): 
            self.info_layout.itemAt(i).widget().deleteLater()
            
        for key, value in file_info.items():
            if key == "유형" and value == "폴더":
                info_label = QLabel(f"{key}: {value}")
                self.info_layout.addWidget(info_label)
            
                file_count, folder_count = self.get_folder_contents_count(file_info["경로"])
                contents_label = QLabel(f"포함된 항목: 파일 {file_count}개, 폴더 {folder_count}개")
                self.info_layout.addWidget(contents_label)
            else:
                info_label = QLabel(f"{key}: {value}")
                self.info_layout.addWidget(info_label)
    
            self.show()

    def clear_info(self):
        self.hide()