from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame
from widgets.file_list import FileList 
from widgets.file_information import FileInformation 

class FileArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)

        self.file_list = FileList(self)
        self.layout.addWidget(self.file_list)
        
        self.add_horizontal_separator()

        self.file_info = FileInformation(self)
        self.layout.addWidget(self.file_info)

        self.setLayout(self.layout)

    def add_horizontal_separator(self):
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.VLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: black;")
        self.layout.addWidget(line_separator)
