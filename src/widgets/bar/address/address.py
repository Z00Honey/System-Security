from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt
from widgets.bar.address.navigation import NavigationWidget
from widgets.bar.address.path import PathBar
from widgets.bar.address.search import SearchBar
from utils.load import load_stylesheet
from utils.secure import SecureFolderManager
from typing import Optional


class AddressBar(QWidget):
    """
    파일 탐색기 상단의 주소 표시줄로, 내비게이션 버튼, 경로 표시, 검색 기능을 포함합니다.
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        secure_manager: Optional[SecureFolderManager] = None
    ) -> None:
        """
        AddressBar 위젯을 초기화합니다.

        Args:
            parent (QWidget, optional): 부모 위젯입니다. 기본값은 None입니다.
            secure_manager (SecureFolderManager, optional): 보안 매니저 객체입니다. 기본값은 None입니다.
        """
        super().__init__(parent)
        self.secure_manager = secure_manager  # 보안 매니저 객체 저장

        # 레이아웃 설정
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # NavigationWidget 생성 및 보안 매니저 전달
        self.navigation_widget = NavigationWidget(
            window=parent,
            secure_manager=self.secure_manager
        )
        self.layout.addWidget(self.navigation_widget, 1)
        self.add_line_separator()

        # PathBar 생성
        self.path_bar = PathBar()
        self.layout.addWidget(self.path_bar, 3)
        self.add_line_separator()

        # SearchBar 생성
        self.search_bar = SearchBar(parent)
        self.layout.addWidget(self.search_bar, 1)

        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("address_bar.css"))

    def add_line_separator(self) -> None:
        """
        수직 구분선을 레이아웃에 추가합니다.
        """
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.VLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: black;")
        self.layout.addWidget(line_separator)