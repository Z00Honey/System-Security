# widgets/file_list.py
from PyQt5.QtWidgets import QTreeView, QAbstractItemView, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from models.file_system_model import FileExplorerModel
import os

class FileList(QWidget):
    path_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.tree_view = QTreeView(self)
        self.setup_ui()
        self.setup_model()
        
        self.layout.addWidget(self.tree_view)
        self.setLayout(self.layout)
        
        self.tree_view.doubleClicked.connect(self.on_double_click)
        
    def setup_ui(self):
        # 기본 UI 설정
        self.tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree_view.setDragEnabled(True)
        self.tree_view.setAcceptDrops(True)
        self.tree_view.setDropIndicatorShown(True)
        self.tree_view.setEditTriggers(QAbstractItemView.EditKeyPressed | QAbstractItemView.SelectedClicked)
        
        # 헤더 설정
        header = self.tree_view.header()
        header.setStretchLastSection(True)
        header.setSectionsMovable(True)
        
        # 트리뷰 설정
        self.tree_view.setRootIsDecorated(False)
        self.tree_view.setItemsExpandable(False)
        self.tree_view.setAlternatingRowColors(True)
        
    def setup_model(self):
        self.model = FileExplorerModel()
        self.tree_view.setModel(self.model)
        
        # 열 크기 설정
        self.tree_view.setColumnWidth(0, 300)  # Name
        self.tree_view.setColumnWidth(1, 150)  # Date Modified
        self.tree_view.setColumnWidth(2, 100)  # Type
        self.tree_view.setColumnWidth(3, 100)  # Size
        
        # 초기 경로 설정
        initial_path = os.path.expanduser("~")
        self.set_current_path(initial_path)
        
    def get_main_window(self):
        parent = self.parent()
        while parent is not None:
            if type(parent).__name__ == 'MainWindow':
                return parent
            parent = parent.parent()
        return None

    def get_navigation_widget(self):
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'address_bar'):
            return main_window.address_bar.navigation_widget
        return None
        
    def set_current_path(self, path):
        if os.path.exists(path):
            index = self.model.index(path)
            self.tree_view.setRootIndex(index)
            self.path_changed.emit(path)
            
            # 경로 표시줄 업데이트
            main_window = self.get_main_window()
            if main_window and hasattr(main_window, 'address_bar'):
                main_window.address_bar.path_bar.update_path(path)
                
    def get_current_path(self):
        return self.model.filePath(self.tree_view.rootIndex())
        
    def on_double_click(self, index):
        path = self.model.filePath(index)
        if os.path.isdir(path):
            nav_widget = self.get_navigation_widget()
            if nav_widget:
                nav_widget.add_to_history(path)
            self.set_current_path(path)