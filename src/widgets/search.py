from PyQt5.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QPushButton, QSizePolicy
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path

class SearchBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.search_input = QLineEdit(self)
        self.search_input.setObjectName("search_bar")
        self.search_input.setPlaceholderText("검색")
        self.search_input.setStyleSheet("border: none;")
        self.search_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.layout.addWidget(self.search_input)

        self.search_button = QPushButton(self)

        self.search_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.search_button.clicked.connect(self.on_search)
        self.layout.addWidget(self.search_button)

        self.set_search_button_icon()

        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("address_bar.css"))

    def set_search_button_icon(self):
        icon_path = image_base_path("search.png")
        self.search_button.setIcon(QIcon(QPixmap(icon_path)))
        self.search_button.setIconSize(QSize(24, 24))
        self.search_button.setFixedSize(30, 30)

    def on_search(self):
        search_text = self.search_input.text()
        print(f"Searching for: {search_text}")

#밑에 검색 로직 추가
