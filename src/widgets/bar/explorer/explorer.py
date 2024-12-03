from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFrame
from widgets.file.area import FileArea
from widgets.bar.explorer.side import Sidebar
from utils.secure import SecureFolderManager  # 수정 제안: 이 임포트는 코드에서 사용되지 않습니다.

class FileExplorerBar(QWidget):
    """
    사이드바와 파일 영역을 포함하는 파일 탐색기 바 위젯입니다.
    """

    def __init__(self, parent: QWidget = None, secure_manager: any = None) -> None:
        """
        FileExplorerBar 위젯을 초기화합니다.

        Args:
            parent (QWidget, optional): 부모 위젯입니다. 기본값은 None입니다.
            secure_manager (any, optional): 보안 매니저 객체입니다. 기본값은 None입니다.
        """
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
        self.file_area = FileArea(self, window=parent, secure_manager=self.secure_manager)
        self.layout.addWidget(self.file_area)

        self.setLayout(self.layout)

    def add_horizontal_separator(self) -> None:
        """
        사이드바와 파일 영역 사이에 수직 구분선을 추가합니다.
        """
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.VLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: black; margin: 0; padding: 0;")
        self.layout.addWidget(line_separator)