import os
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from utils.load import load_stylesheet
from PyQt5.QtCore import Qt

# 주석: 더 정확한 타입 힌트를 위해 필요하다면 typing 모듈에서 Optional을 임포트할 수 있습니다.
# from typing import Optional

class PathBar(QWidget):
    """
    현재 파일 경로를 표시하고 업데이트하는 위젯입니다.
    """

    def __init__(self, parent=None) -> None:
        """
        PathBar 위젯을 초기화합니다.

        Args:
            parent (QWidget, optional): 부모 위젯입니다. 기본값은 None입니다.
        """
        super().__init__(parent)

        # 레이아웃 설정
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(5)

        # 사용자 홈 디렉토리 경로로 초기 경로 설정
        user_home_path = os.path.expanduser("~")
        self.path_label = QLabel(user_home_path)
        self.path_label.setObjectName("path_label")
        self.path_label.setFixedHeight(40)

        self.layout.addWidget(self.path_label)
        self.layout.setAlignment(self.path_label, Qt.AlignCenter)

        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("address_bar.css"))

    def update_path(self, new_path: str) -> None:
        """
        경로 표시를 업데이트합니다.

        Args:
            new_path (str): 새로 표시할 경로입니다.
        """
        self.path_label.setText(new_path)

    def get_path(self) -> str:
        """
        현재 표시된 경로를 반환합니다.

        Returns:
            str: 현재 경로 텍스트입니다.
        """
        return self.path_label.text()