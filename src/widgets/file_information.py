from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame

class FileInformation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)

        self.add_horizontal_separator()

        self.title_label = QLabel("파일 정보", self)
        self.layout.addWidget(self.title_label)

        self.add_horizontal_separator()

        # 밑에 내용 비워두기 (추후에 파일 정보 추가 예정)
        self.layout.addStretch()

        self.setLayout(self.layout)

    def add_horizontal_separator(self):
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.HLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: black;")
        self.layout.addWidget(line_separator)
