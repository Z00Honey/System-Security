from PyQt5.QtWidgets import QTreeView, QAbstractItemView, QWidget, QVBoxLayout, QHeaderView, QSizePolicy, QApplication, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData, QUrl
from models.file_system_model import FileExplorerModel
from widgets.file_information import FileInformation
from PyQt5.QtGui import QCursor
import shutil
import os

def set_clipboard_files(file_paths, move=False):
    """
    클립보드에 파일을 복사 또는 잘라내기 위한 데이터를 설정합니다.
    
    :param file_paths: 클립보드에 복사할 파일 경로 리스트
    :param move: 잘라내기 여부 (True: 잘라내기, False: 복사)
    """
    # QMimeData 생성
    mime_data = QMimeData()
    urls = [QUrl.fromLocalFile(path) for path in file_paths]
    mime_data.setUrls(urls)
    
    # 'Preferred DropEffect' 설정 (잘라내기: MOVE(2), 복사: COPY(1))
    if move:
        mime_data.setData('Preferred DropEffect', b'\x02\x00\x00\x00')  # MOVE
    else:
        mime_data.setData('Preferred DropEffect', b'\x01\x00\x00\x00')  # COPY
    
    # 클립보드에 설정
    clipboard = QApplication.clipboard()
    clipboard.setMimeData(mime_data)
    
    # 디버깅 출력

class FileList(QWidget):
    path_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.tree_view = QTreeView(self)
        self.cut_files = set()
        self.tree_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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
        self.tree_view.setAcceptDrops(False)
        self.tree_view.setDropIndicatorShown(False)
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

        self.tree_view.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree_view.header().setStretchLastSection(False)
        self.tree_view.header().setSectionResizeMode(1, QHeaderView.Fixed)
        self.tree_view.header().setSectionResizeMode(2, QHeaderView.Fixed)
        self.tree_view.header().setSectionResizeMode(3, QHeaderView.Fixed)
        
        # 열 크기 설정
        self.tree_view.setColumnWidth(0, 300)  # Name
        self.tree_view.setColumnWidth(1, 150)  # Date Modified
        self.tree_view.setColumnWidth(2, 100)  # Type
        self.tree_view.setColumnWidth(3, 100)  # Size
        self.tree_view.keyPressEvent = self.keyPressEvent
        
        # 초기 경로 설정
        initial_path = os.path.expanduser("~")
        self.set_current_path(initial_path)

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
            file_area.file_info.show_file_info(file_info)

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            self.copySelectedFiles(cut=False)

        elif event.key() == Qt.Key_X and event.modifiers() == Qt.ControlModifier:
            self.copySelectedFiles(cut=True)

        elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            self.pasteFiles()
        elif event.key() == Qt.Key_Delete:
            self.deleteSelectedFiles()
        else:
            super().keyPressEvent(event)

    def deleteSelectedFiles(self):
        selected_indexes = self.tree_view.selectionModel().selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "삭제 오류", "삭제할 파일이 선택되지 않았습니다.")
            return

        # 선택된 파일 경로 목록 가져오기
        file_paths = []
        for index in selected_indexes:
            if index.column() == 0:
                file_path = self.model.filePath(index)
                file_paths.append(file_path)

        if not file_paths:
            QMessageBox.warning(self, "삭제 오류", "유효한 파일 경로가 없습니다.")
            return

        # 확인 메시지 표시
        reply = QMessageBox.question(
            self,
            "삭제 확인",
            "선택한 파일을 정말로 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.No:
            return  # 사용자가 '아니오'를 선택한 경우 작업 취소

        # 파일 삭제 수행
        errors = []
        for file_path in file_paths:
            try:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # 폴더 삭제
                else:
                    os.remove(file_path)  # 파일 삭제
            except Exception as e:
                errors.append(f"Error deleting {file_path}: {e}")

        # 오류 메시지 처리
        if errors:
            QMessageBox.critical(self, "삭제 오류", "\n".join(errors))
        else:
            QMessageBox.information(self, "삭제 완료", "선택한 파일이 성공적으로 삭제되었습니다.")

        # UI 업데이트 (필요하면 새로고침 구현)
        self.tree_view.model().layoutChanged.emit()

    def copySelectedFiles(self, cut=False):
        selected_indexes = self.tree_view.selectionModel().selectedIndexes()
        if not selected_indexes:
            return

        file_paths = []
        for index in selected_indexes:
            if index.column() == 0:
                file_path = self.model.filePath(index)
                file_paths.append(file_path)

        if not file_paths:
            return

        set_clipboard_files(file_paths, move=cut)

        if cut:
            self.cut_files.update(file_paths)

    def pasteFiles(self):
        """
        클립보드에 있는 파일들을 현재 선택된 디렉토리에 붙여넣기 합니다.
        복사(Copy) 또는 이동(Move) 작업을 수행합니다.
        """
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if not mime_data.hasUrls():
            QMessageBox.warning(self, "붙여넣기 오류", "클립보드에 붙여넣을 파일이 없습니다.")
            return

        urls = mime_data.urls()
        file_paths = [url.toLocalFile() for url in urls if url.isLocalFile()]

        if not file_paths:
            QMessageBox.warning(self, "붙여넣기 오류", "클립보드에 유효한 파일 경로가 없습니다.")
            return

        # 'Preferred DropEffect'를 확인하여 복사 또는 이동 결정
        drop_effect_format = 'Preferred DropEffect'
        if mime_data.hasFormat(drop_effect_format):
            drop_effect = mime_data.data(drop_effect_format)
            operation = 'move' if drop_effect == b'\x02\x00\x00\x00' else 'copy'
        else:
            operation = 'copy'

        # 대상 디렉토리 결정
        selected_indexes = self.tree_view.selectionModel().selectedIndexes()
        if selected_indexes:
            index = selected_indexes[0]
            target_dir = self.model.filePath(index)
            if not os.path.isdir(target_dir):
                target_dir = os.path.dirname(target_dir)
        else:
            target_dir = self.model.rootPath()

        if not target_dir:
            main_window = self.get_main_window()
            if main_window and hasattr(main_window, 'address_bar'):
                target_dir = main_window.address_bar.path_bar.get_path()
            else:
                target_dir = os.path.expanduser("~")  # 기본 경로로 사용자 홈 디렉토리를 사용

        errors = []
        files_processed = 0  # 성공적으로 처리된 파일 수

        for source in file_paths:
            try:
                destination = os.path.join(target_dir, os.path.basename(source))

                # 소스와 대상이 동일한 파일인지 확인
                if os.path.abspath(source) == os.path.abspath(destination):
                    QMessageBox.warning(self, "붙여넣기 경고", f"소스와 대상이 동일합니다: {source}")
                    continue  # 다음 파일로 넘어감

                if os.path.exists(destination):
                    # 파일이나 디렉토리가 이미 존재하는 경우 덮어쓰기 여부를 묻는다
                    reply = QMessageBox.question(
                        self,
                        '덮어쓰기 확인',
                        f"'{os.path.basename(destination)}'이(가) 이미 존재합니다.\n덮어쓰시겠습니까?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        continue  # 사용자가 '아니오'를 선택한 경우 해당 파일을 건너뜁니다.

                    # 덮어쓰기 진행: 기존 파일/폴더 삭제
                    if os.path.isdir(destination):
                        shutil.rmtree(destination)
                    else:
                        os.remove(destination)

                # 복사 또는 이동 작업 수행
                if operation == 'copy':
                    if os.path.isdir(source):
                        shutil.copytree(source, destination)
                    else:
                        shutil.copy2(source, destination)
                elif operation == 'move':
                    shutil.move(source, destination)

                files_processed += 1  # 성공적으로 처리된 파일 수 증가

            except Exception as e:
                errors.append(f"Error {operation}ing {source} to {destination}: {e}")

        # 오류가 발생한 경우 사용자에게 알림
        if errors:
            QMessageBox.critical(self, "붙여넣기 오류", "\n".join(errors))

        # 작업이 성공적으로 완료된 경우 완료 메시지 표시
        if files_processed > 0:
            action_str = "이동" if operation == "move" else "복사"
            QMessageBox.information(self, "붙여넣기 완료", f"{files_processed}개의 파일을 성공적으로 {action_str}했습니다.")

        # 이동 작업의 경우 잘라내기 상태 초기화
        if operation == 'move':
            self.cut_files.clear()