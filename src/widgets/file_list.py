from PyQt5.QtWidgets import QTreeView, QAbstractItemView, QWidget, QVBoxLayout, QHeaderView, QMessageBox  # QMessageBox 임포트 추가
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor
from models.file_system_model import FileExplorerModel
from widgets.file_information import FileInformation
import os

class FileList(QWidget):
    path_changed = pyqtSignal(str)
    
    def __init__(self, parent=None, secure_manager=None):
        super().__init__(parent)
        self.secure_manager = secure_manager  # secure_manager 객체 받기

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.tree_view = QTreeView(self)
        self.setup_ui()
        self.setup_model()
        
        self.layout.addWidget(self.tree_view)
        self.setLayout(self.layout)
        
        self.tree_view.doubleClicked.connect(self.on_double_click)
        
        # 파일 정보 다이얼로그 초기화
        self.tree_view.clicked.connect(self.show_file_info)
        self.file_info = FileInformation(self)

    def setup_ui(self):
        self.tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree_view.setDragEnabled(True)
        self.tree_view.setAcceptDrops(True)
        self.tree_view.setDropIndicatorShown(True)
        self.tree_view.setEditTriggers(QAbstractItemView.EditKeyPressed | QAbstractItemView.SelectedClicked)
        
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
        self.model = FileExplorerModel()
        self.tree_view.setModel(self.model)

        self.tree_view.header().setSectionResizeMode(0, QHeaderView.Stretch)  # 이름 열
        self.tree_view.header().setStretchLastSection(False)
        self.tree_view.header().setSectionResizeMode(1, QHeaderView.Fixed)    # 수정 날짜
        self.tree_view.header().setSectionResizeMode(2, QHeaderView.Fixed)    # 유형
        self.tree_view.header().setSectionResizeMode(3, QHeaderView.Fixed)    # 크기
        
        # 열 크기 설정
        self.tree_view.setColumnWidth(0, 300)  # 이름
        self.tree_view.setColumnWidth(1, 150)  # 수정 날짜
        self.tree_view.setColumnWidth(2, 100)  # 유형
        self.tree_view.setColumnWidth(3, 100)  # 크기
        
        # 초기 경로 설정
        initial_path = os.path.expanduser("~")
        self.set_current_path(initial_path)  # 초기 경로 설정
        
    def show_file_info(self, index):
        file_path = self.model.filePath(index)
        file_info = {
            "이름": self.model.fileName(index),
            "경로": file_path,
            "유형": "폴더" if self.model.isDir(index) else f"{self.model.fileInfo(index).suffix().upper()} 파일",
            "수정한 날짜": self.model.fileInfo(index).lastModified().toString("yyyy-MM-dd hh:mm:ss"),
            "크기": self.model.size(index) if not self.model.isDir(index) else "폴더"
        }
        # FileArea의 file_info 위젯 가져오기
        file_area = self.parent()
        if hasattr(file_area, 'file_info'):
            file_area.file_info.show_file_info(file_info)  # 파일 정보 표시

    def get_main_window(self):
        parent = self.parent()
        while parent is not None:
            if type(parent).__name__ == 'MainWindow':
                return parent
            parent = parent.parent()
        return None

    def get_navigation_widget(self):
        # MainWindow에서 내비게이션 위젯 가져오기
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'address_bar'):
            return main_window.address_bar.navigation_widget
        return None
        
    def set_current_path(self, path):
        if os.path.exists(path):  # 경로가 실제로 존재할 때만 실행
            secure_folder_path = os.path.normpath(self.secure_manager.secure_folder_path) if self.secure_manager else None
            current_path = os.path.normpath(path)

            # 보안 폴더 접근 시 인증 요구
            if secure_folder_path and secure_folder_path in current_path and not self.secure_manager.authenticated:
                self.secure_manager.authenticate()  # 인증 시도
                if not self.secure_manager.authenticated:
                   return  # 인증 실패 시 이동 중단

            # 보안 폴더에서 벗어나면 인증 해제
            if self.secure_manager and self.secure_manager.authenticated and secure_folder_path not in current_path:
                self.secure_manager.authenticated = False
                QMessageBox.information(self, "인증 해제", "보안 폴더에서 벗어났습니다. 인증이 해제됩니다.")
                path = os.path.expanduser("~")  # 첫 화면 경로로 이동 (홈 디렉토리)
            
            # 경로 이동 처리
            index = self.model.index(path)
            self.tree_view.setRootIndex(index)
            self.path_changed.emit(path)  # 경로 변경 신호 발생
            
            # 경로 표시줄 업데이트
            main_window = self.get_main_window()
            if main_window and hasattr(main_window, 'address_bar'):
                main_window.address_bar.path_bar.update_path(path)  # 주소 표시줄 업데이트

                
    def get_current_path(self):
        return self.model.filePath(self.tree_view.rootIndex())
        
    def on_double_click(self, index):
        path = self.model.filePath(index)
        if os.path.isdir(path):
            nav_widget = self.get_navigation_widget()
            if nav_widget:
                nav_widget.add_to_history(path)
            self.set_current_path(path)  # 경로 이동
