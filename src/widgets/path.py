import os
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from utils.load import load_stylesheet
from PyQt5.QtCore import Qt

class PathBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(5)

        # 사용자의 홈 디렉토리 경로 가져오기
        user_home_path = os.path.expanduser("~")
        self.path_label = QLabel(user_home_path)
        self.path_label.setObjectName("path_label")  # QLabel에 이름을 설정합니다.

        # QLabel의 높이를 설정하여 중앙 정렬 보장
        self.path_label.setFixedHeight(40)  # 필요에 따라 높이를 조정

        # 레이아웃에 QLabel 추가
        self.layout.addWidget(self.path_label)
        self.layout.setAlignment(self.path_label, Qt.AlignCenter)  # QLabel을 중앙 정렬

        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("path.css"))

    # 경로 업데이트 메서드
    def update_path(self, new_path: str):
        self.path_label.setText(new_path)  # 업데이트된 경로만 표시



