import sys
import os
import ctypes
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeView, QListWidget, QVBoxLayout, QWidget, QToolBar, QAction, QLineEdit, QHBoxLayout, QListWidgetItem,
    QTabWidget, QFileSystemModel, QMessageBox, QSplitter, QDockWidget, QHeaderView, QMenu, QActionGroup, QTabBar, QInputDialog
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDir, Qt, QSortFilterProxyModel, QEvent

class SortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSortCaseSensitivity(Qt.CaseInsensitive)

class FileExplorerTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.address_bar = QLineEdit(self)
        self.address_bar.setPlaceholderText("주소 입력")
        self.address_bar.returnPressed.connect(self.navigate_to_address)
        layout.addWidget(self.address_bar)

        self.file_view = QTreeView(self)
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.proxy_model = SortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.file_view.setModel(self.proxy_model)
        self.file_view.setSortingEnabled(True)
        self.file_view.setRootIndex(self.proxy_model.mapFromSource(self.model.index(QDir.rootPath())))
        self.file_view.doubleClicked.connect(self.open_file_or_folder)
        self.file_view.header().setSectionsClickable(True)
        self.file_view.header().sectionClicked.connect(self.header_clicked)
        self.file_view.header().setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_view.header().customContextMenuRequested.connect(self.show_header_context_menu)
        self.file_view.setContextMenuPolicy(Qt.CustomContextMenu)
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

        self.visible_columns = [0, 1, 2, 3]  # 기본적으로 보이는 컬럼

        # DLL 로드
        '''
        self.file_operations_dll = ctypes.CDLL("../../build/file_operations.dll")
        self.compress_dll = ctypes.CDLL("../../build/compress.dll")
        self.virus_scan_dll = ctypes.CDLL("../../build/virus_scan.dll")
        self.header_check_dll = ctypes.CDLL("../../build/header_check.dll")
        self.lock_dll = ctypes.CDLL("../../build/lock.dll")
        self.hide_dll = ctypes.CDLL("../../build/hide.dll")
        self.properties_dll = ctypes.CDLL("../../build/properties.dll")
        '''

    def navigate_to(self, path):
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
            self.file_operations_dll.open_file(path.encode('utf-8'))

    def add_to_history(self, path):
        if self.current_index == -1 or path != self.history[self.current_index]:
            self.current_index += 1
            self.history = self.history[:self.current_index]
            self.history.append(path)

    def header_clicked(self, logical_index):
        if self.current_sort_column == logical_index:
            if self.current_sort_order == Qt.AscendingOrder:
                self.current_sort_order = Qt.DescendingOrder
            else:
                self.current_sort_order = Qt.AscendingOrder
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
            if column == 0:  # '이름' 컬럼은 항상 체크되어 있고 비활성화
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

        new_folder_action = menu.addAction("새 폴더 만들기")
        new_file_action = menu.addAction("새 파일 만들기")
        menu.addSeparator()

        if index.isValid():
            source_index = self.proxy_model.mapToSource(index)
            file_path = self.model.filePath(source_index)

            delete_action = menu.addAction("삭제")
            rename_action = menu.addAction("이름변경")
            open_action = menu.addAction("열기")
            menu.addSeparator()
            
            compress_action = menu.addAction("압축")
            virus_scan_action = menu.addAction("바이러스 검사")
            header_check_action = menu.addAction("헤더검사")
            lock_action = menu.addAction("잠금")
            hide_action = menu.addAction("숨기기")
            properties_action = menu.addAction("속성")

        action = menu.exec_(self.file_view.viewport().mapToGlobal(pos))

        if action == new_folder_action:
            self.create_new_folder(self.model.filePath(self.file_view.rootIndex()))
        elif action == new_file_action:
            self.create_new_file(self.model.filePath(self.file_view.rootIndex()))
        elif index.isValid():
            if action == delete_action:
                self.file_operations_dll.delete_file(file_path.encode('utf-8'))
            elif action == rename_action:
                self.file_operations_dll.rename_file(file_path.encode('utf-8'))
            elif action == open_action:
                self.file_operations_dll.open_file(file_path.encode('utf-8'))
            elif action == compress_action:
                self.compress_dll.compress_file(file_path.encode('utf-8'))
            elif action == virus_scan_action:
                self.virus_scan_dll.scan_file(file_path.encode('utf-8'))
            elif action == header_check_action:
                self.header_check_dll.check_header(file_path.encode('utf-8'))
            elif action == lock_action:
                self.lock_dll.lock_file(file_path.encode('utf-8'))
            elif action == hide_action:
                self.hide_dll.hide_file(file_path.encode('utf-8'))
            elif action == properties_action:
                self.properties_dll.show_properties(file_path.encode('utf-8'))

    def create_new_folder(self, parent_path):
        self.file_operations_dll.create_new_folder(parent_path.encode('utf-8'))

    def create_new_file(self, parent_path):
        self.file_operations_dll.create_new_file(parent_path.encode('utf-8'))

class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setElideMode(Qt.ElideRight)

class FileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("[일만집중하조] 파일 탐색기")
        self.setGeometry(100, 100, 1000, 700)

        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        toolbar = QToolBar("메인 도구 모음")
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        toolbar.setMovable(False)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(CustomTabBar())
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tab_widget)

        actions = [
            ('new.png', '새 탭', self.add_new_tab),
            ('back.png', '뒤로', self.go_back),
            ('front.png', '앞으로', self.go_forward),
            ('leftup.png', '상위 폴더', self.go_up)
        ]

        for icon, text, func in actions:
            action = QAction(QIcon(f'icon/{icon}'), text, self)
            action.triggered.connect(func)
            toolbar.addAction(action)

        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("파일 검색")
        self.search_bar.returnPressed.connect(self.search_files)
        self.search_bar.setFixedWidth(150)
        toolbar.addWidget(self.search_bar)

        self.sidebar = QListWidget()

        sidebar_items = [
            ("terminal.png", "내 PC"),
            ("downloads.png", "다운로드"),
            ("apps.png", "바탕화면"),
            ("folder.png", "문서"),
            ("gallary.png", "사진"),
            ("minimize.png", "테스트1")
        ]
        
        for icon, text in sidebar_items:
            self.sidebar.addItem(QListWidgetItem(QIcon(f'icon/{icon}'), text))
        self.sidebar.clicked.connect(self.sidebar_item_clicked)

        self.sidebar_dock = QDockWidget("즐겨찾기", self)
        self.sidebar_dock.setWidget(self.sidebar)
        self.sidebar_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.sidebar_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        self.addDockWidget(Qt.RightDockWidgetArea, self.sidebar_dock)

        # sidebar_dock 크기 조절 및 숨김 기능 설정
        self.sidebar_dock.installEventFilter(self)
        self.sidebar_dock_hidden = False

        self.statusBar().showMessage("Test for File Explorer GUI | 2024-09-28 20:00 | last tester : 이서준")
        self.add_new_tab()

    def eventFilter(self, obj, event):
        if obj == self.sidebar_dock and event.type() == QEvent.Resize:
            self.handle_sidebar_resize(event.size().width())
        return super().eventFilter(obj, event)

    def handle_sidebar_resize(self, width):
        if width < 100 and not self.sidebar_dock_hidden:
            self.sidebar_dock.hide()
            self.sidebar_dock_hidden = True

    def add_new_tab(self):
        new_tab = FileExplorerTab(self)
        index = self.tab_widget.addTab(new_tab, "새 탭")
        self.tab_widget.setCurrentIndex(index)
        new_tab.navigate_to(QDir.homePath())

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            self.close()

    def sidebar_item_clicked(self, index):
        item = self.sidebar.currentItem().text()
        paths = {
            "내 PC": QDir.rootPath(),
            "다운로드": os.path.join(QDir.homePath(), "Downloads"),
            "바탕화면": os.path.join(QDir.homePath(), "Desktop"),
            "문서": os.path.join(QDir.homePath(), "Documents"),
            "사진": os.path.join(QDir.homePath(), "Pictures"),
            "테스트1": os.path.join(QDir.homePath(), "source")
        }
        path = paths.get(item, QDir.rootPath())
        self.tab_widget.currentWidget().navigate_to(path)

    def go_back(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab.current_index > 0:
            current_tab.current_index -= 1
            current_tab.navigate_to(current_tab.history[current_tab.current_index])

    def go_forward(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab.current_index < len(current_tab.history) - 1:
            current_tab.current_index += 1
            current_tab.navigate_to(current_tab.history[current_tab.current_index])

    def go_up(self):
        current_tab = self.tab_widget.currentWidget()
        current_path = current_tab.address_bar.text()
        parent_path = os.path.dirname(current_path)
        current_tab.navigate_to(parent_path)

    def search_files(self):
        current_tab = self.tab_widget.currentWidget()
        search_term = self.search_bar.text()
        current_path = current_tab.model.filePath(current_tab.file_view.rootIndex())
        for root, dirs, files in os.walk(current_path):
            for name in files:
                if search_term.lower() in name.lower():
                    full_path = os.path.join(root, name)
                    self.statusBar().showMessage(f"경로 {full_path}", 5000)
                    return
        self.statusBar().showMessage("파일을 찾을 수 없습니다.", 3000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileExplorer()
    window.show()
    sys.exit(app.exec_())