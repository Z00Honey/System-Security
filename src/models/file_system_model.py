from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtCore import Qt, QDir

class FileExplorerModel(QFileSystemModel):
    def __init__(self):
        super().__init__()
        self.setRootPath(QDir.rootPath())
        self.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.Hidden)
        
        # 표시할 열 설정
        self.setReadOnly(False)
        
    def columnCount(self, parent=None):
        return 4  # 이름, 크기, 유형, 수정한 날짜
        
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return "이름"
            elif section == 1:
                return "크기"
            elif section == 2:
                return "유형"
            elif section == 3:
                return "수정한 날짜"
        return super().headerData(section, orientation, role) 