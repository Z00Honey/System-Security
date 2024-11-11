from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QScrollArea, QHeaderView
from PyQt5.QtCore import Qt

from utils.load import load_stylesheet

class FileList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget(self)
        self.table.setRowCount(5)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Date Modified", "Type", "Size"])

        # 마지막 열이 부모 크기에 맞게 늘어나도록 설정
        self.table.horizontalHeader().setStretchLastSection(True)

        # 각 열의 너비를 설정하여 수평 스크롤이 생기지 않도록
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # 여백 없애기
        self.layout.setSpacing(0)  # 아이템 간의 간격도 없애기

        # QScrollArea를 사용하여 스크롤을 추가
        scroll_area = QScrollArea(self)
        scroll_area.setWidget(self.table)
        scroll_area.setWidgetResizable(True) 
        scroll_area.setContentsMargins(0, 0, 0, 0) 
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 수평 스크롤 숨기기

        self.layout.addWidget(scroll_area) 

        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("file_list.css"))
        self.setObjectName("file_list")
