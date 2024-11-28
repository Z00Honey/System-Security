from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QSizePolicy
from widgets.file_list import FileList 
from widgets.file_information import FileInformation
from widgets.search_list_widget import SearchListWidget

class FileArea(QWidget):
    def __init__(self, parent=None, window=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # FileList 추가
        self.file_list = FileList(self)
        self.file_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.file_list, 1)
        
        # 구분선 추가 및 저장
        self.separator_after_file_list = self.add_horizontal_separator()

        # SearchListWidget 추가
        self.search_result_list = SearchListWidget(self)
        self.search_result_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.search_result_list.hide()
        self.layout.addWidget(self.search_result_list, 1)

        # 두 번째 구분선 추가
        self.separator_after_search_results = self.add_horizontal_separator()

        # FileInformation 추가
        self.file_info = FileInformation(self)
        self.file_info.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.layout.addWidget(self.file_info)

        self.setLayout(self.layout)

    def add_horizontal_separator(self):
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.HLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: black; margin: 0; padding: 0;")
        line_separator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.layout.addWidget(line_separator)
        return line_separator  # 구분선을 반환하여 저장할 수 있도록 함

    def get_status_search_results(self):
        return self.search_result_list.isHidden()

    def get_status_file_list(self):
        return self.file_list.isHidden()

    def show_search_results(self):
        # FileList와 그 아래 구분선 숨기기
        self.file_list.hide()
        self.file_list.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.file_list.updateGeometry()
        
        self.separator_after_file_list.hide()

        # SearchListWidget 보이기
        self.search_result_list.show()
        self.search_result_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.search_result_list.updateGeometry()

        # 레이아웃 업데이트
        self.layout.update()
        self.updateGeometry()

    def show_file_list(self):
        # SearchListWidget 숨기기
        self.search_result_list.hide()
        self.search_result_list.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.search_result_list.updateGeometry()

        # FileList와 그 아래 구분선 보이기
        self.separator_after_file_list.show()
        
        self.file_list.show()
        self.file_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.file_list.updateGeometry()

        # 레이아웃 업데이트
        self.layout.update()
        self.updateGeometry()
