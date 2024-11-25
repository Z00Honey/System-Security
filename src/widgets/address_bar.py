from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt
from widgets.navigation import NavigationWidget
from widgets.path import PathBar
from widgets.search import SearchBar
from utils.load import load_stylesheet

class AddressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.navigation_widget = NavigationWidget()
        self.layout.addWidget(self.navigation_widget, 1)
        self.add_line_separator()

        self.path_bar = PathBar()
        self.layout.addWidget(self.path_bar, 3)
        self.add_line_separator()  

        self.search_bar = SearchBar()
        self.layout.addWidget(self.search_bar, 1)

        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("address_bar.css"))

    def add_line_separator(self) -> None:
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.VLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: black;")
        self.layout.addWidget(line_separator)