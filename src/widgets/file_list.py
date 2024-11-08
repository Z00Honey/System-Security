from PyQt5.QtWidgets import QTreeView, QAbstractItemView
from PyQt5.QtCore import Qt, pyqtSignal
from models.file_system_model import FileExplorerModel

class FileListView(QTreeView):
    path_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_model()
        
    def setup_ui(self):
        # 기본 UI 설정
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setEditTriggers(QAbstractItemView.EditKeyPressed | QAbstractItemView.SelectedClicked)
        
        # 열 크기 설정
        self.setColumnWidth(0, 300)  # 이름
        self.setColumnWidth(1, 100)  # 크기
        self.setColumnWidth(2, 150)  # 유형
        self.setColumnWidth(3, 150)  # 수정한 날짜
        
    def setup_model(self):
        self.model = FileExplorerModel()
        self.setModel(self.model)
        
        # 불필요한 열 숨기기
        for i in range(1, self.model.columnCount()):
            self.setColumnHidden(i, False)
            
    def set_current_path(self, path):
        index = self.model.index(path)
        self.setRootIndex(index)
        self.path_changed.emit(path)
        
    def mouseDoubleClickEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid():
            path = self.model.filePath(index)
            if self.model.isDir(index):
                self.set_current_path(path)
            else:
                # 파일 실행 로직 추가
                pass 