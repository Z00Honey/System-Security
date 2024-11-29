import os
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from utils.load import load_stylesheet
from PyQt5.QtCore import Qt

class PathBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(5)

        user_home_path = os.path.expanduser("~")
        self.path_label = QLabel(user_home_path)
        self.path_label.setObjectName("path_label") 

        self.path_label.setFixedHeight(40) 

        self.layout.addWidget(self.path_label)
        self.layout.setAlignment(self.path_label, Qt.AlignCenter)  

        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("address_bar.css"))

    def update_path(self, new_path: str):
        self.path_label.setText(new_path)



