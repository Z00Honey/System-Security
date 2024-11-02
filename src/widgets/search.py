from PyQt5.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtGui import QPixmap
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

        search_icon_label = QLabel(self)
        pixmap = QPixmap(image_base_path("search.png"))  
        search_icon_label.setPixmap(pixmap)
        self.layout.addWidget(search_icon_label)

        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("search.css"))  


