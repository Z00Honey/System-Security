from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFrame
from widgets.file_area import FileArea
from widgets.titlebar.sidebar import Sidebar
from utils.secure import SecureFolderManager

class FileExplorerBar(QWidget):
    def __init__(self, parent=None, secure_manager=None):
        super().__init__(parent)

        self.secure_manager = secure_manager  # secure_manager 객체를 받음

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Sidebar에 secure_manager 전달
        self.sidebar = Sidebar(self, secure_manager=self.secure_manager)
        self.layout.addWidget(self.sidebar)

        self.add_horizontal_separator()

        # FileArea에 secure_manager 전달
        self.file_area = FileArea(self, secure_manager=self.secure_manager)
        self.layout.addWidget(self.file_area)

        self.setLayout(self.layout)

    def add_horizontal_separator(self):
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.VLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: black; margin: 0; padding: 0;") 
        self.layout.addWidget(line_separator)
