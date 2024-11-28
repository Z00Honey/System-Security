from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame
from widgets.file_list import FileList
from widgets.file_information import FileInformation

class FileArea(QWidget):
    def __init__(self, parent=None, secure_manager=None):
        super().__init__(parent)

        self.secure_manager = secure_manager  # secure_manager 객체 받기

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.file_list = FileList(self)
        self.layout.addWidget(self.file_list, 1)        
        
        self.add_horizontal_separator()

        self.file_info = FileInformation(self)
        self.layout.addWidget(self.file_info)

        self.setLayout(self.layout)

    def add_horizontal_separator(self):
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.HLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: black; margin: 0; padding: 0;")
        self.layout.addWidget(line_separator)
