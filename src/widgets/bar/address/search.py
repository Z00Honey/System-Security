from PyQt5.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QPushButton, QSizePolicy
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path
from ...file.file_search import file_search
from ... import global_variable
from os.path import join  # 이 임포트는 사용되지 않습니다. 필요 시 제거를 고려해주세요.
import os
from datetime import datetime


class SearchBar(QWidget):
    """
    파일 검색 기능을 제공하는 검색 바 위젯입니다.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        SearchBar 위젯을 초기화합니다.

        Args:
            parent (QWidget, optional): 부모 위젯입니다. 기본값은 None입니다.
        """
        super().__init__(parent)
        self.parent = parent

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.search_input = QLineEdit(self)
        self.search_input.setObjectName("search_bar")
        self.search_input.setPlaceholderText("검색")
        self.search_input.setStyleSheet("border: none;")
        self.search_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.layout.addWidget(self.search_input)

        self.search_button = QPushButton(self)
        self.search_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.search_button.clicked.connect(self.on_search)
        self.layout.addWidget(self.search_button)

        self.set_search_button_icon()

        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("address_bar.css"))

    def set_search_button_icon(self) -> None:
        """
        검색 버튼의 아이콘을 설정합니다.
        """
        icon_path = image_base_path("search.png")
        self.search_button.setIcon(QIcon(QPixmap(icon_path)))
        self.search_button.setIconSize(QSize(24, 24))
        self.search_button.setFixedSize(30, 30)

    def on_search(self) -> None:
        """
        검색 버튼 클릭 시 호출되어 파일 검색을 수행합니다.
        """
        filename = self.search_input.text()
        if not filename: ###수정
            return
        directory = global_variable.GLOBAL_CURRENT_PATH

        for path in file_search(directory, filename):
            self.parent.search_result_addItem(path)

        self.parent.show_search_results()

    def show_file_info(self, file_path: str) -> None:
        """
        파일 정보를 부모 위젯에 표시합니다.

        Args:
            file_path (str): 정보를 표시할 파일의 경로입니다.
        """
        if os.path.exists(file_path):
            # 이름 (파일 또는 폴더 이름)
            name = os.path.basename(file_path)

            # 유형 (폴더 또는 파일 확장자)
            if os.path.isdir(file_path):
                file_type = "폴더"
                size = "폴더"
            else:
                extension = os.path.splitext(file_path)[1][1:].upper()
                file_type = f"{extension} 파일" if extension else "파일"
                # 크기 (바이트 단위)
                size_in_bytes = os.path.getsize(file_path)
                size = f"{size_in_bytes} 바이트"

            # 수정한 날짜 (형식: yyyy-MM-dd hh:mm:ss)
            timestamp = os.path.getmtime(file_path)
            last_modified = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

            file_info = {
                "이름": name,
                "경로": file_path,
                "유형": file_type,
                "수정한 날짜": last_modified,
                "크기": size,
            }
        else:
            # 경로가 존재하지 않을 경우 처리
            file_info = {
                "이름": "알 수 없음",
                "경로": file_path,
                "유형": "알 수 없음",
                "수정한 날짜": "알 수 없음",
                "크기": "알 수 없음",
            }

        # FileArea의 file_info 위젯 가져오기
        file_area = self.parent()
        if hasattr(file_area, 'file_info'):
            file_area.file_info.show_file_info(file_info)