from PyQt5.QtWidgets import (
    QMenu, 
    QAction, 
    QWidget, 
    QLineEdit,
    QTreeView, 
    QTabWidget, 
    QVBoxLayout, 
    QMessageBox, 
    QActionGroup,
    QFileSystemModel, 
)
from PyQt5.QtCore import QSortFilterProxyModel, QDir, Qt
import os
from .password_manager import PasswordManager
from .ProcessAES import AESManager

# <정렬 및 필터링을 위한 사용자 정의 모델 클래스>
class SortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSortCaseSensitivity(Qt.CaseInsensitive)

# <파일 탐색기 탭 생성 클래스>
class Tab_FileExplorer(QWidget):
    def __init__(self, parent=None, secure_manager=None):
        super().__init__(parent)
        self.secure_manager = secure_manager
        self.pwd=PasswordManager()
        self.AES=AESManager()
        self.init_ui()

        # DLL 관련 객체 초기화
        self.file_operations_dll = getattr(self, 'file_operations_dll', None)
        self.compress_dll = getattr(self, 'compress_dll', None)
        self.virus_scan_dll = getattr(self, 'virus_scan_dll', None)
        self.header_check_dll = getattr(self, 'header_check_dll', None)
        self.properties_dll = getattr(self, 'properties_dll', None)

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 주소 입력바 설정
        self.address_bar = QLineEdit(self)
        self.address_bar.setPlaceholderText("주소 입력")
        self.address_bar.returnPressed.connect(self.navigate_to_address)
        
        layout.addWidget(self.address_bar)

        self.file_view = QTreeView(self)

        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())

        self.proxy_model = SortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)

        self.file_view.setSortingEnabled(True)
        self.file_view.setModel(self.proxy_model)
        self.file_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_view.setRootIndex(self.proxy_model.mapFromSource(self.model.index(QDir.rootPath())))

        self.file_view.doubleClicked.connect(self.open_file_or_folder)
        self.file_view.header().setSectionsClickable(True)
        self.file_view.header().sectionClicked.connect(self.header_clicked)
        self.file_view.header().setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_view.header().customContextMenuRequested.connect(self.show_header_context_menu)
        self.file_view.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.file_view)

        self.file_view.setColumnWidth(0, 300)  # 이름 (Name)
        self.file_view.setColumnWidth(1, 100)  # 크기 (Size)
        self.file_view.setColumnWidth(2, 100)  # 유형 (Type)
        self.file_view.setColumnWidth(3, 150)  # 수정한 날짜 (Date Modified)

        self.model.setReadOnly(False)
        self.model.setFilter(QDir.AllEntries | QDir.Hidden | QDir.System)

        self.history = []
        self.current_index = -1

        self.current_sort_column = 0
        self.current_sort_order = Qt.AscendingOrder

        self.visible_columns = [0, 1, 2, 3]

    def navigate_to(self, path):
        secure_folder_path = os.path.normpath(self.secure_manager.secure_folder_path) if self.secure_manager else None
        current_path = os.path.normpath(path)

        # 보안 폴더 접근 시 인증 요구
        if secure_folder_path and secure_folder_path in current_path and not self.secure_manager.authenticated:
            self.secure_manager.authenticate()
            if not self.secure_manager.authenticated:
                return

        # 보안 폴더에서 벗어날 경우 첫 화면으로 이동
        if self.secure_manager and self.secure_manager.authenticated and secure_folder_path not in current_path:
            self.secure_manager.authenticated = False

            QMessageBox.information(self, "인증 해제", "보안 폴더에서 벗어납니다. 인증이 해제됩니다.")
            path = QDir.homePath()  # 첫 화면 경로로 이동

        # 경로 이동 처리
        source_index = self.model.index(path)
        proxy_index = self.proxy_model.mapFromSource(source_index)
        self.file_view.setRootIndex(proxy_index)
        self.address_bar.setText(path)
        self.add_to_history(path)
        self.update_tab_name(path)


    def navigate_to_address(self):
        path = self.address_bar.text()
        if os.path.exists(path):
            self.navigate_to(path)
        else:
            QMessageBox.warning(self, "주소를 찾을 수 없습니다.", "입력하신 주소를 다시 확인해주세요.")

    def open_file_or_folder(self, index):
        source_index = self.proxy_model.mapToSource(index)
        path = self.model.filePath(source_index)
        if os.path.isdir(path):
            self.navigate_to(path)
        else:
            if self.file_operations_dll:
                try:
                    self.file_operations_dll.open_file(path.encode('utf-8'))
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"파일을 여는 동안 오류가 발생했습니다: {str(e)}")
            else:
                QMessageBox.critical(self, "Error", "파일 열기 기능이 설정되지 않았습니다.")

    def add_to_history(self, path):
        if self.current_index == -1 or path != self.history[self.current_index]:
            self.current_index += 1
            self.history = self.history[:self.current_index]
            self.history.append(path)

    def header_clicked(self, logical_index):
        if self.current_sort_column == logical_index:
            self.current_sort_order = Qt.DescendingOrder if self.current_sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            self.current_sort_column = logical_index
            self.current_sort_order = Qt.AscendingOrder

        self.file_view.sortByColumn(self.current_sort_column, self.current_sort_order)

    def show_header_context_menu(self, pos):
        menu = QMenu(self)
        header = self.file_view.header()

        column_group = QActionGroup(self)
        column_group.setExclusive(False)

        columns = [
            ("이름", 0),
            ("크기", 1),
            ("유형", 2),
            ("수정한 날짜", 3),
        ]

        for text, column in columns:
            action = QAction(text, self)
            action.setCheckable(True)
            action.setChecked(column in self.visible_columns)
            action.setData(column)

            if column == 0:
                action.setEnabled(False)
            else:
                action.triggered.connect(self.toggle_column)
            column_group.addAction(action)
            menu.addAction(action)

        menu.exec_(self.file_view.header().mapToGlobal(pos))

    def toggle_column(self):
        action = self.sender()
        if action:
            column = action.data()
            if action.isChecked():
                if column not in self.visible_columns:
                    self.visible_columns.append(column)
                    self.file_view.setColumnHidden(column, False)
            else:
                if column in self.visible_columns:
                    self.visible_columns.remove(column)
                    self.file_view.setColumnHidden(column, True)

    def update_tab_name(self, path):
        tab_widget = self.parent().parent()
        if isinstance(tab_widget, QTabWidget):
            index = tab_widget.indexOf(self)
            tab_widget.setTabText(index, os.path.basename(path) or "루트")

    def show_context_menu(self, pos):
        index = self.file_view.indexAt(pos)
        menu = QMenu(self)

        try:
            if index.isValid():
                source_index = self.proxy_model.mapToSource(index)
                file_path = self.model.filePath(source_index)

                # secure_action: 잠금 또는 해제 메뉴 추가 (authenticated 상태에 따라 변경)
                if not self.secure_manager.authenticated:
                    secure_action = menu.addAction("잠금")
                else:
                    secure_action = menu.addAction("해제")

                # 추가 동작 메뉴
                reset_action = menu.addAction("초기화")

                # 사용자 선택 처리
                action = menu.exec_(self.file_view.viewport().mapToGlobal(pos))

                if action:
                    if action == secure_action:
                        if not self.secure_manager.authenticated:
                            # 잠금 수행
                            try:
                                self.secure_manager.lock(file_path)
                            except Exception as e:
                                QMessageBox.critical(self, "Error", f"파일 잠금 중 오류가 발생했습니다: {str(e)}")
                        else:
                            # 해제 수행
                            try:
                                self.secure_manager.unlock(file_path)
                            except Exception as e:
                                QMessageBox.critical(self, "Error", f"파일 해제 중 오류가 발생했습니다: {str(e)}")
                    elif action == reset_action:
                        self.pwd.reset()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"컨텍스트 메뉴를 표시하는 동안 오류가 발생했습니다: {str(e)}")


    def create_new_folder(self, parent_path):
        if self.file_operations_dll:
            try:
                self.file_operations_dll.create_new_folder(parent_path.encode('utf-8'))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"새 폴더 만들기 중 오류가 발생했습니다: {str(e)}")
        else:
            QMessageBox.critical(self, "Error", "새 폴더 만들기 기능이 설정되지 않았습니다.")

    def create_new_file(self, parent_path):
        if self.file_operations_dll:
            try:
                self.file_operations_dll.create_new_file(parent_path.encode('utf-8'))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"새 파일 만들기 중 오류가 발생했습니다: {str(e)}")
        else:
            QMessageBox.critical(self, "Error", "새 파일 만들기 기능이 설정되지 않았습니다.")
