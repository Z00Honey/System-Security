from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path

class NavigationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        self.back_button = self.create_button("back.png", "뒤로 가기")
        self.forward_button = self.create_button("forward.png", "앞으로 가기")
        self.up_button = self.create_button("up.png", "위로 가기")
        self.refresh_button = self.create_button("refresh.png", "새로 고침")

        self.layout.addWidget(self.back_button)
        self.layout.addWidget(self.forward_button)
        self.layout.addWidget(self.up_button)
        self.layout.addWidget(self.refresh_button)

        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("navigation.css"))
        self.setObjectName("navigation_widget")


    def create_button(self, icon_name, tooltip):
        button = QPushButton()
        icon_path = image_base_path(icon_name)
        button.setIcon(QIcon(icon_path))
        button.setToolTip(tooltip)
        
        icon_size = 20
        button_size = 40
        button.setFixedSize(button_size, button_size)
        button.setIconSize(QSize(icon_size, icon_size))
        return button
