import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication,
    QTreeView,
    QAbstractItemView,
    QWidget,
    QVBoxLayout,
    QHeaderView,
    QFileIconProvider,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal, QFileInfo
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class SearchListWidget(QWidget):
    path_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.tree_view = QTreeView(self)
        self.tree_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setup_ui()
        self.setup_model()

        self.layout.addWidget(self.tree_view)
        self.setLayout(self.layout)

        # 클릭 이벤트 연결
        self.tree_view.clicked.connect(self.on_item_clicked)

    def setup_ui(self):
        self.tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree_view.setDragEnabled(True)
        self.tree_view.setAcceptDrops(False)

        self.tree_view.setDropIndicatorShown(False)
        self.tree_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = self.tree_view.header()
        header.setStretchLastSection(True)
        header.setSectionsMovable(True)

        self.tree_view.setRootIsDecorated(False)
        self.tree_view.setItemsExpandable(False)
        self.tree_view.setAlternatingRowColors(True)

        self.tree_view.setStyleSheet("""
            QTreeView::item { 
                height: 35px;
                padding: 5px;
            }
        """)

    def setup_model(self):
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Name", "Date Modified", "Type", "Size"])
        self.tree_view.setModel(self.model)

        # 열 크기 설정
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree_view.header().setStretchLastSection(False)
        self.tree_view.header().setSectionResizeMode(1, QHeaderView.Fixed)
        self.tree_view.header().setSectionResizeMode(2, QHeaderView.Fixed)
        self.tree_view.header().setSectionResizeMode(3, QHeaderView.Fixed)

        self.tree_view.setColumnWidth(0, 300)  # Name
        self.tree_view.setColumnWidth(1, 150)  # Date Modified
        self.tree_view.setColumnWidth(2, 100)  # Type
        self.tree_view.setColumnWidth(3, 100)  # Size

    def set_paths(self, paths):
        """주어진 파일 및 폴더 경로 리스트를 모델에 로드합니다."""
        self.model.removeRows(0, self.model.rowCount())  # 기존 항목 삭제

        for path in paths:
            if os.path.exists(path):
                self.add_item(path)
            else:
                # 경로가 유효하지 않을 경우 처리
                name_item = QStandardItem(os.path.basename(path))
                name_item.setForeground(Qt.red)
                date_item = QStandardItem("N/A")
                type_item = QStandardItem("Invalid Path")
                size_item = QStandardItem("N/A")
                for item in [name_item, date_item, type_item, size_item]:
                    item.setEditable(False)
                self.model.appendRow([name_item, date_item, type_item, size_item])

    def add_item(self, path):
        """파일 또는 폴더를 모델에 추가하고 아이콘을 설정합니다."""
        # 이름 설정
        name = os.path.basename(path)
        name_item = QStandardItem(name)
        name_item.setData(path, Qt.UserRole)  # 파일 경로를 데이터로 저장

        # 수정 날짜
        last_modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")
        date_item = QStandardItem(last_modified)

        # 아이콘 제공자 초기화
        icon_provider = QFileIconProvider()
        file_info = QFileInfo(path)
        icon = icon_provider.icon(file_info)

        # 타입과 크기 설정
        if os.path.isdir(path):
            type_str = "Folder"
            size_str = "-"
        else:
            ext = os.path.splitext(path)[1][1:].upper()
            type_str = f"{ext} File" if ext else "File"
            size_str = self.human_readable_size(os.path.getsize(path))

        type_item = QStandardItem(type_str)
        size_item = QStandardItem(size_str)

        # 아이콘 설정
        name_item.setIcon(icon)

        # 편집 불가능하도록 설정
        for item in [name_item, date_item, type_item, size_item]:
            item.setEditable(False)

        self.model.appendRow([name_item, date_item, type_item, size_item])

    def on_item_clicked(self, index):
        """항목을 클릭했을 때 파일 정보를 표시합니다."""
        # 첫 번째 열의 인덱스로 변환
        index = index.sibling(index.row(), 0)
        item = self.model.itemFromIndex(index)
        if item is not None:
            file_path = item.data(Qt.UserRole)
            self.show_file_info(file_path)

    def show_file_info(self, file_path):
        """파일 경로를 받아 파일 정보를 표시합니다."""
        if os.path.exists(file_path):
            # 이름
            name = os.path.basename(file_path)

            # 유형 및 크기
            if os.path.isdir(file_path):
                file_type = "폴더"
                size = "폴더"
            else:
                extension = os.path.splitext(file_path)[1][1:].upper()
                file_type = f"{extension} 파일" if extension else "파일"
                size_in_bytes = os.path.getsize(file_path)
                size = self.human_readable_size(size_in_bytes)

            # 수정한 날짜
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
        while file_area is not None and not hasattr(file_area, 'file_info'):
            file_area = file_area.parent()
        if file_area is not None and hasattr(file_area, 'file_info'):
            file_area.file_info.show_file_info(file_info)

    @staticmethod
    def human_readable_size(size):
        """바이트 단위 크기를 사람이 읽을 수 있는 형식으로 변환합니다."""
        for unit in ["바이트", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    def clear(self):
        self.tree_view.model().clear()
        self.tree_view.model().setHorizontalHeaderLabels(["Name", "Date Modified", "Type", "Size"])