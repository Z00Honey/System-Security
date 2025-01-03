from PyQt5.QtWidgets import QTreeView, QAbstractItemView, QWidget, QVBoxLayout, QHeaderView, QSizePolicy, QApplication, QMessageBox, QMenu, QAction, QProgressDialog, QLineEdit
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData, QUrl, QProcess
from models.file_system_model import FileExplorerModel
from widgets.file.information import FileInformation
from PyQt5.QtGui import QCursor, QDesktopServices, QPixmap, QIcon
import shutil, subprocess
import os
from utils.secure import TaskRunner
from utils.load import image_base_path

def set_clipboard_files(file_paths: list[str], move: bool = False) -> None:
    """
    Sets clipboard data for copying or cutting files.

    Args:
        file_paths (list[str]): List of file paths to copy or cut.
        move (bool): Flag to indicate cutting (True) or copying (False). Defaults to False.
    """
    mime_data = QMimeData()
    urls = [QUrl.fromLocalFile(path) for path in file_paths]
    mime_data.setUrls(urls)

    # Set 'Preferred DropEffect' (Cut: MOVE(2), Copy: COPY(1))
    if move:
        mime_data.setData('Preferred DropEffect', b'\x02\x00\x00\x00')  # MOVE
    else:
        mime_data.setData('Preferred DropEffect', b'\x01\x00\x00\x00')  # COPY

    clipboard = QApplication.clipboard()
    clipboard.setMimeData(mime_data)

class RenameLineEdit(QLineEdit):
    """인라인 이름 변경을 위한 QLineEdit 위젯"""
    def __init__(self, old_name, parent=None):
        super().__init__(old_name, parent)
        self.old_name = old_name

    def focusOutEvent(self, event):
        """포커스를 잃었을 때 원래 이름으로 복원"""
        self.setText(self.old_name)
        super().focusOutEvent(event)

# Class declarations are unchanged but re-structured for alignment
class FileList(QWidget):
    add_to_favorites_signal = pyqtSignal(str)  # 새로운 신호 추가
    path_changed = pyqtSignal(str)

    def __init__(self, parent: QWidget = None, secure_manager: any = None) -> None:
        super().__init__(parent)
        self.secure_manager = secure_manager  # Secure manager object

        # Layout configuration
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Configure QTreeView
        self.tree_view = QTreeView(self)
        self.cut_files: set[str] = set()
        self.tree_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setup_ui()
        self.setup_model()

        self.layout.addWidget(self.tree_view)
        self.setLayout(self.layout)

        self.tree_view.doubleClicked.connect(self.on_double_click)

        # Initialize file information dialog
        self.tree_view.clicked.connect(self.show_file_info)
        self.file_info = FileInformation(self)

    def setup_ui(self) -> None:
        """Configures the UI settings for the QTreeView."""
        self.tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree_view.setDragEnabled(True)
        self.tree_view.setAcceptDrops(False)
        self.tree_view.setDropIndicatorShown(False)
        self.tree_view.setEditTriggers(
            QAbstractItemView.EditKeyPressed | QAbstractItemView.SelectedClicked
        )

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

        # 컨텍스트 메뉴 활성화
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)

    def setup_model(self) -> None:
        """Initializes and configures the file system model."""
        self.model = FileExplorerModel()
        self.tree_view.setModel(self.model)

        self.tree_view.header().setSectionResizeMode(0, QHeaderView.Stretch)  # Name column
        self.tree_view.header().setStretchLastSection(False)
        self.tree_view.header().setSectionResizeMode(1, QHeaderView.Fixed)    # Modified date
        self.tree_view.header().setSectionResizeMode(2, QHeaderView.Fixed)    # Type
        self.tree_view.header().setSectionResizeMode(3, QHeaderView.Fixed)    # Size

        # Set column widths
        self.tree_view.setColumnWidth(0, 300)  # Name
        self.tree_view.setColumnWidth(1, 150)  # Modified date
        self.tree_view.setColumnWidth(2, 100)  # Type
        self.tree_view.setColumnWidth(3, 100)  # Size

        self.tree_view.keyPressEvent = self.keyPressEvent

        # Set initial path
        initial_path = os.path.expanduser("~")
        self.set_current_path(initial_path)

    def show_file_info(self, index) -> None:
        """Displays file information in the parent widget."""
        file_path = self.model.filePath(index)
        file_info = {
            "Name": self.model.fileName(index),
            "Path": file_path,
            "Type": "Folder" if self.model.isDir(index) else f"{self.model.fileInfo(index).suffix().upper()} File",
            "Last Modified": self.model.fileInfo(index).lastModified().toString("yyyy-MM-dd hh:mm:ss"),
            "Size": self.model.size(index) if not self.model.isDir(index) else "Folder",
        }

        parent_widget = self.parent()
        if hasattr(parent_widget, 'file_info'):
            parent_widget.file_info.show_file_info(file_info)


    def get_main_window(self) -> QWidget:
        """
        Retrieves the main window by traversing parent widgets.

        Returns:
            QWidget: The main window widget, or None if not found.
        """
        parent = self.parent()
        while parent is not None:
            if type(parent).__name__ == 'MainWindow':
                return parent
            parent = parent.parent()
        return None

    def get_navigation_widget(self) -> QWidget:
        """
        Retrieves the navigation widget from the main window.

        Returns:
            QWidget: The navigation widget, or None if not found.
        """
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'address_bar'):
            return main_window.address_bar.navigation_widget
        return None

    def set_current_path(self, path: str) -> None:
        """
        Sets the current path in the file explorer view.

        Args:
            path (str): The path to set as the current directory.
        """
        if os.path.exists(path):  # Only proceed if the path exists
            secure_folder_path = os.path.normpath(self.secure_manager.secure_folder_path) if self.secure_manager else None
            current_path = os.path.normpath(path)

            # Require authentication for secure folders
            if secure_folder_path and secure_folder_path in current_path and not self.secure_manager.authenticated:
                self.secure_manager.authenticate()
                if not self.secure_manager.authenticated:
                    return  # Abort if authentication fails

            # De-authenticate when leaving secure folders
            if self.secure_manager and self.secure_manager.authenticated and secure_folder_path not in current_path:
                self.secure_manager.authenticated = False
                QMessageBox.information(self, "De-authenticated", "You have exited the secure folder. Authentication has been cleared.")
                path = os.path.expanduser("~")  # Default to home directory

            # Update the file explorer view
            index = self.model.index(path)
            self.tree_view.setRootIndex(index)
            self.path_changed.emit(path)

            # Update the address bar
            main_window = self.get_main_window()
            if main_window and hasattr(main_window, 'address_bar'):
                main_window.address_bar.path_bar.update_path(path)

    def get_current_path(self) -> str:
        """
        Retrieves the current path displayed in the file explorer.

        Returns:
            str: The current directory path.
        """
        return self.model.filePath(self.tree_view.rootIndex())

    def on_double_click(self, index) -> None:
        """
        Handles double-click events to navigate into directories or open files.

        Args:
            index: The index of the double-clicked item.
        """
        path = self.model.filePath(index)
        if os.path.isdir(path):
            nav_widget = self.get_navigation_widget()
            if nav_widget:
                nav_widget.add_to_history(path)
                self.set_current_path(path)
        else:
            try:
                if os.name == 'nt':
                    os.startfile(path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to open file: {str(e)}")

    def keyPressEvent(self, event: any) -> None:
        """
        Handles key press events for file operations like copy, cut, paste, and delete.

        Args:
            event: The key press event object.
        """
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

    def deleteSelectedFiles(self) -> None:
        """
        Deletes the selected files or directories after user confirmation.
        """
        selected_indexes = self.tree_view.selectionModel().selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "Delete Error", "No files or directories selected for deletion.")
            return

        # Retrieve file paths from selected indexes
        file_paths = []
        for index in selected_indexes:
            if index.column() == 0:
                file_path = self.model.filePath(index)
                file_paths.append(file_path)

        if not file_paths:
            QMessageBox.warning(self, "Delete Error", "No valid file paths found.")
            return

        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete the selected files or directories?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.No:
            return  # Abort if the user chooses "No"

        # Perform deletion
        errors = []
        for file_path in file_paths:
            try:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Delete directory
                else:
                    os.remove(file_path)  # Delete file
            except Exception as e:
                errors.append(f"Error deleting {file_path}: {e}")

        # Display errors or success message
        if errors:
            QMessageBox.critical(self, "Delete Error", "\n".join(errors))
        else:
            QMessageBox.information(self, "Delete Success", "Selected files or directories deleted successfully.")

        # Refresh the UI if needed
        self.tree_view.model().layoutChanged.emit()

    def copySelectedFiles(self, cut: bool = False) -> None:
        """
        Copies or cuts the selected files to the clipboard.

        Args:
            cut (bool): True to cut files, False to copy them. Defaults to False.
        """
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

        # If cutting, add files to the cut files set
        if cut:
            self.cut_files.update(file_paths)

    def pasteFiles(self) -> None:
        """
        Pastes the files from the clipboard to the current directory.
        Handles both copy and move operations.
        """
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if not mime_data.hasUrls():
            QMessageBox.warning(self, "Paste Error", "No files in the clipboard to paste.")
            return

        urls = mime_data.urls()
        file_paths = [url.toLocalFile() for url in urls if url.isLocalFile()]

        if not file_paths:
            QMessageBox.warning(self, "Paste Error", "No valid file paths found in the clipboard.")
            return

        # Determine the operation (copy or move) based on 'Preferred DropEffect'
        drop_effect_format = 'Preferred DropEffect'
        if mime_data.hasFormat(drop_effect_format):
            drop_effect = mime_data.data(drop_effect_format)
            operation = 'move' if drop_effect == b'\x02\x00\x00\x00' else 'copy'
        else:
            operation = 'copy'

        # Determine the target directory
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
                target_dir = os.path.expanduser("~")  # Default to home directory

        errors = []
        files_processed = 0  # Count of successfully processed files

        for source in file_paths:
            try:
                destination = os.path.join(target_dir, os.path.basename(source))

                # Check if source and destination are the same
                if os.path.abspath(source) == os.path.abspath(destination):
                    QMessageBox.warning(self, "Paste Warning", f"Source and destination are the same: {source}")
                    continue

                if os.path.exists(destination):
                    # Ask for overwrite confirmation
                    reply = QMessageBox.question(
                        self,
                        'Overwrite Confirmation',
                        f"'{os.path.basename(destination)}' already exists.\nDo you want to overwrite it?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        continue

                    # Delete the existing file/folder before overwriting
                    if os.path.isdir(destination):
                        shutil.rmtree(destination)
                    else:
                        os.remove(destination)

                # Perform the copy or move operation
                if operation == 'copy':
                    if os.path.isdir(source):
                        shutil.copytree(source, destination)
                    else:
                        shutil.copy2(source, destination)
                elif operation == 'move':
                    shutil.move(source, destination)

                files_processed += 1

            except Exception as e:
                errors.append(f"Error {operation}ing {source} to {destination}: {e}")

        # Display errors or success message
        if errors:
            QMessageBox.critical(self, "Paste Error", "\n".join(errors))

        if files_processed > 0:
            action_str = "moved" if operation == "move" else "copied"
            QMessageBox.information(self, "Paste Success", f"{files_processed} files successfully {action_str}.")

        # Clear the cut files set after move
        if operation == 'move':
            self.cut_files.clear()

    def show_context_menu(self, position) -> None:
        """우클릭 컨텍스트 메뉴를 표시합니다."""
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return

        is_dir = self.model.isDir(index)
        file_path = self.model.filePath(index)
        
        menu = QMenu(self)
        
        # 공통 액션 생성
        open_action = QAction("열기", self)
        open_action.triggered.connect(lambda: self.open_item(file_path))
        
        # 폴더/파일 전용 액션
        if is_dir:
            favorite_action = QAction("즐겨찾기", self)
            favorite_action.triggered.connect(lambda: self.add_to_favorites(file_path))
        else:
            open_with_action = QAction("연결프로그램", self)
            open_with_action.triggered.connect(lambda: self.open_with(file_path))

    
        
        if not is_dir:
            security_scan_action = QAction("확장자 검사", self)
            security_scan_action.triggered.connect(lambda: self.security_scan(file_path))
        
        virus_scan_action = QAction("바이러스 검사", self)
        virus_scan_action.triggered.connect(lambda: self.virus_scan(file_path))
        if self.secure_manager.authenticated:
            lock_action = QAction("해제", self)
            lock_action.triggered.connect(lambda: self.lock_item(file_path))
        else:
            lock_action = QAction("잠금", self)
            lock_action.triggered.connect(lambda: self.lock_item(file_path))

        
        # 편집 관련 액션
        cut_action = QAction("잘라내기", self)
        cut_action.triggered.connect(lambda: self.copySelectedFiles(cut=True))
        
        copy_action = QAction("복사", self)
        copy_action.triggered.connect(lambda: self.copySelectedFiles(cut=False))
        
        delete_action = QAction("삭제", self)
        delete_action.triggered.connect(self.deleteSelectedFiles)
        
        rename_action = QAction("이름바꾸기", self)
        rename_action.triggered.connect(lambda: self.rename_item(index))
        
        properties_action = QAction("속성", self)
        properties_action.triggered.connect(lambda: self.show_properties(file_path))
        
        # 메뉴 구성
        menu.addAction(open_action)
        if is_dir:
            menu.addAction(favorite_action)
        else:
            menu.addAction(open_with_action)
        
        menu.addSeparator()
        
        if not is_dir:
            menu.addAction(security_scan_action)
        menu.addAction(virus_scan_action)
        menu.addAction(lock_action)
        
        menu.addSeparator()
        
        menu.addAction(cut_action)
        menu.addAction(copy_action)
        menu.addAction(delete_action)
        menu.addAction(rename_action)
        #menu.addAction(properties_action)
        
        # 메뉴 표시
        menu.exec_(QCursor.pos())

    def open_item(self, path: str) -> None:
        """항목을 엽니다."""
        if os.path.isdir(path):
            self.set_current_path(path)
        else:
            self.on_double_click(self.tree_view.currentIndex())

    def open_with(self, path: str) -> None:
        """파일을 열 프로그램을 선택합니다."""
        if os.name == 'nt':
            subprocess.run(['cmd', '/c', 'start', 'shell:::{:}', path])
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def add_to_favorites(self, path: str) -> None:
        """즐겨찾기에 경로를 추가합니다."""
        if os.path.exists(path):
            self.add_to_favorites_signal.emit(path)
        else:
            QMessageBox.warning(self, "오류", "존재하지 않는 경로입니다.")

    def security_scan(self, path: str) -> None:
        """선택된 파일에 대해 확장자 검사를 실행합니다."""
        if os.path.isdir(path):
            QMessageBox.warning(self, "경고", "파일만 검사할 수 있습니다.")
            return

        # 확인 메시지 표시
        message_box = QMessageBox(self)
        message_box.setWindowTitle("확장자 검사")
        message_box.setText("선택한 파일에 대한 포맷 및 확장자 불일치 검사를 진행하시겠습니까?")
        
        custom_icon_path = image_base_path("shield.png")
        custom_icon = QPixmap(custom_icon_path)
        message_box.setIconPixmap(custom_icon)
        
        message_box.setStandardButtons(QMessageBox.NoButton)
        yes_button = message_box.addButton("예", QMessageBox.YesRole)
        no_button = message_box.addButton("아니요", QMessageBox.NoRole)

        message_box.exec_()
        if message_box.clickedButton() == yes_button:
            from utils.analysis import analyze_file
            result = analyze_file(path)
            
            # 결과 메시지 표시
            result_box = QMessageBox(self)
            result_box.setWindowTitle("확장자 검사 결과")
            result_box.setText(result)
            result_box.setIconPixmap(custom_icon)
            result_box.setStandardButtons(QMessageBox.NoButton)
            ok_button = result_box.addButton("확인", QMessageBox.AcceptRole)
            result_box.exec_()

    def virus_scan(self, path: str) -> None:
        """선택된 파일 또는 폴더에 대해 바이러스 검사를 실행합니다."""
        if os.path.isdir(path):
            folder_content = os.listdir(path)
            files_only = [f for f in folder_content if os.path.isfile(os.path.join(path, f))]

            if not files_only:
                QMessageBox.information(self, "정보", "선택한 폴더에 파일이 없습니다.")
                return

        # 확인 메시지 표시
        message_box = QMessageBox(self)
        message_box.setWindowTitle("바이러스 검사")
        message_box.setText("선택한 파일/폴더에 대한 바이러스 검사를 진행하시겠습니까?")

        custom_icon_path = image_base_path("shield.png")
        custom_icon = QPixmap(custom_icon_path)
        message_box.setIconPixmap(custom_icon)

        message_box.setStandardButtons(QMessageBox.NoButton)
        yes_button = message_box.addButton("예", QMessageBox.YesRole)
        no_button = message_box.addButton("아니요", QMessageBox.NoRole)

        message_box.exec_()
        if message_box.clickedButton() == yes_button:
            self.start_virus_scan(path)

    def start_virus_scan(self, path: str) -> None:
        """바이러스 검사를 시작합니다."""
        from utils.virus_scan import VirusScanThread
        
        self.progress_dialog = QProgressDialog("검사 중...", "취소", 0, 100, self)
        self.progress_dialog.setWindowTitle("바이러스 검사")
        self.progress_dialog.setWindowModality(True)

        self.scan_thread = VirusScanThread(path)
        self.scan_thread.finished.connect(self.on_scan_finished)
        self.scan_thread.error.connect(self.on_scan_error)
        self.scan_thread.progress.connect(self.update_progress)

        self.progress_dialog.canceled.connect(self.scan_thread.terminate)
        self.scan_thread.start()
        self.progress_dialog.show()

    def update_progress(self, current: int, total: int) -> None:
        """검사 진행 상황을 업데이트합니다."""
        if hasattr(self, 'progress_dialog'):
            progress = int((current / total) * 100)
            self.progress_dialog.setValue(progress)
            self.progress_dialog.setLabelText(f"검사 중... ({current}/{total})")

    def on_scan_finished(self, result: str) -> None:
        """바이러스 검사가 완료되었을 때 호출됩니다."""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
            
            # 결과 메시지 표시
            message_box = QMessageBox(self)
            message_box.setWindowTitle("검사 완료")
            message_box.setText(result)
            
            custom_icon_path = image_base_path("shield.png")
            custom_icon = QPixmap(custom_icon_path)
            message_box.setIconPixmap(custom_icon)
            
            message_box.setStandardButtons(QMessageBox.NoButton)
            ok_button = message_box.addButton("확인", QMessageBox.AcceptRole)
            message_box.exec_()
            
            # 리소스 정리
            self.scan_thread.deleteLater()
            delattr(self, 'scan_thread')
            delattr(self, 'progress_dialog')

    def on_scan_error(self, error_message: str) -> None:
        """바이러스 검사 중 오류가 발생했을 때 호출됩니다."""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
            QMessageBox.critical(self, "오류", f"검사 중 오류가 발생했습니다:\n{error_message}")
            
            # 리소스 정리
            self.scan_thread.deleteLater()
            delattr(self, 'scan_thread')
            delattr(self, 'progress_dialog')

    def lock_item(self, path: str) -> None:
        """항목을 잠급니다."""
        size_in_bytes = self.get_size(path)
        if self.secure_manager.pwd_mgr.AESkey is None:  # None으로 체크
            QMessageBox.warning(self, "Error", "AES 키가 설정되지 않았습니다.")
            return  # 키가 없으면 더 이상 실행하지 않음
        
        size_limit = 5 * 1024**3  # 5GB
        if size_in_bytes > size_limit:
            QMessageBox.warning(self, "Error", "파일 또는 폴더 크기가 5GB를 초과하여 작업을 수행할 수 없습니다.")
            return  # 크기 초과 시 실행 중단

        # 인증 여부 확인
        if not self.secure_manager.authenticated:
            # 잠금 메시지창
            reply = QMessageBox.question(
                self, "잠금", "해당 폴더(파일)를 잠금 처리 하시겠습니까?",
                QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                try:
                    TaskRunner.run(self.secure_manager.lock, path)
                    QMessageBox.information(self, "잠금 완료", "폴더(파일)가 성공적으로 잠금 처리되었습니다.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"잠금 중 오류 발생: {str(e)}")
        else:
            # 해제 메시지창
            reply = QMessageBox.question(
                self, "해제", "해당 폴더(파일)를 잠금 해제 하시겠습니까?",
                QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                try:
                    TaskRunner.run(self.secure_manager.unlock, path)
                    QMessageBox.information(self, "해제 완료", "폴더(파일)가 성공적으로 잠금 해제되었습니다.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"해제 중 오류 발생: {str(e)}")

        pass

    def rename_item(self, index) -> None:
        """항목의 이름을 인라인으로 변경합니다."""
        if not index.isValid():
            return

        # 기존 인라인 위젯 제거
        if hasattr(self, 'inline_widget'):
            self.remove_inline_widget()

        old_name = self.model.fileName(index)
        self.inline_widget = RenameLineEdit(old_name)
        self.inline_widget.setFixedWidth(200)
        self.inline_widget.returnPressed.connect(lambda: self.finish_rename(index))
        self.inline_widget.editingFinished.connect(self.remove_inline_widget)

        self.tree_view.setIndexWidget(index, self.inline_widget)
        self.inline_widget.setFocus()
        self.inline_widget.selectAll()

    def finish_rename(self, index) -> None:
        """이름 변경을 완료하고 파일시스템에 적용합니다."""
        if not hasattr(self, 'inline_widget'):
            return

        new_name = self.inline_widget.text()
        if new_name and new_name != self.inline_widget.old_name:
            old_path = self.model.filePath(index)
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            
            try:
                os.rename(old_path, new_path)
                self.model.setRootPath(self.model.rootPath())  # 뷰 갱신
            except OSError as e:
                QMessageBox.warning(self, "오류", f"이름 변경 중 오류가 발생했습니다: {str(e)}")

        self.remove_inline_widget()

    def remove_inline_widget(self) -> None:
        """인라인 편집 위젯을 제거합니다."""
        if hasattr(self, 'inline_widget'):
            self.tree_view.setIndexWidget(self.tree_view.currentIndex(), None)
            delattr(self, 'inline_widget')

    def show_properties(self, path: str) -> None:
        """항목의 속성을 표시합니다."""
        # TODO: 속성 창 표시 기능 구현
        pass
    def get_size(self,path):
        """파일 또는 폴더 크기를 계산"""
        if os.path.isfile(path):
            return os.path.getsize(path)  # 파일 크기 반환
        elif os.path.isdir(path):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if not os.path.islink(file_path):
                        total_size += os.path.getsize(file_path)
            return total_size  # 폴더 크기 반환
        else:
            raise ValueError(f"Invalid path: {path} is neither a file nor a folder.")
