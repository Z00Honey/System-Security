from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtCore import Qt, QDateTime, QDir
import os

class FileExplorerModel(QFileSystemModel):
    def __init__(self):
        super().__init__()
        self.setRootPath("")
        self.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        self._headers = ["Name", "Date Modified", "Type", "Size"]

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
        
    def data(self, index, role):
        if role == Qt.DisplayRole:
            if index.column() == 1:  # Date Modified
                return QDateTime.fromSecsSinceEpoch(
                    self.fileInfo(index).lastModified().toSecsSinceEpoch()
                ).toString("yyyy-MM-dd hh:mm")
            elif index.column() == 2:  # Type
                if self.isDir(index):
                    return "Folder"
                return self.fileInfo(index).suffix().upper() + " File"
            elif index.column() == 3:  # Size
                if self.isDir(index):
                    return ""
                size = self.size(index)
                return self.format_size(size)
        return super().data(index, role)
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"