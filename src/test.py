import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)
from PyQt5.QtCore import Qt


class FileInfoApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Info Viewer")
        self.setGeometry(100, 100, 800, 600)

        # 메인 위젯과 레이아웃 설정
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 버튼 추가
        self.show_button = QPushButton("Show File Info")
        self.show_button.clicked.connect(self.show_file_info)
        self.layout.addWidget(self.show_button)

        # 샘플 파일 데이터
        self.file_data = [
            ["C:/example/file1.txt", "2024-11-28 14:32", "file", "1.2 KB"],
            ["C:/example/folder", "2024-11-27 10:15", "folder", "-"],
            ["C:/example/file2.jpg", "2024-11-26 08:45", "file", "2.5 MB"],
        ]

        # 파일 정보 위젯 참조용 속성 추가
        self.file_info_widget = None

    def show_file_info(self):
        # 새로운 위젯 생성
        self.file_info_widget = QWidget()
        self.file_info_widget.setWindowTitle("File Info")
        self.file_info_widget.setGeometry(150, 150, 700, 400)

        layout = QVBoxLayout(self.file_info_widget)

        # 테이블 생성
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["File Path", "Last Modified", "Type", "Size"])
        table.setRowCount(len(self.file_data))

        # 테이블에 데이터 채우기
        for row, file_info in enumerate(self.file_data):
            for col, value in enumerate(file_info):
                table.setItem(row, col, QTableWidgetItem(value))

        # 테이블 설정
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # 편집 불가
        table.resizeColumnsToContents()
        table.resizeRowsToContents()

        layout.addWidget(table)

        # 새 창 띄우기
        self.file_info_widget.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileInfoApp()
    window.show()
    sys.exit(app.exec_())
