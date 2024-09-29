
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeView, QListWidget, QVBoxLayout, QWidget, QToolBar, QAction, QLineEdit, QHBoxLayout, QListWidgetItem,
    QTabWidget, QFileSystemModel, QMessageBox, QSplitter, QDockWidget, QHeaderView, QMenu, QActionGroup, QTabBar, QInputDialog
)
from PyQt5.QtCore import QDir, Qt, QSortFilterProxyModel, QEvent
from PyQt5.QtGui import QIcon

from .tabs.FileExplorer import Tab_FileExplorer
from .icons import (
    SIDEBAR_ITEMS
)

import os
import sys

class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setElideMode(Qt.ElideRight)

class FileExplorer(QMainWindow):
    def __init__(self):

        self.image_basepath = "./icon"

        super().__init__()
        self.SettingUserInterface()

    def SettingUserInterface(self):
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
            action = QAction(QIcon(f'{self.image_basepath}/tab/{icon}'), text, self)
            action.triggered.connect(func)
            toolbar.addAction(action)

        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("파일 검색")
        self.search_bar.returnPressed.connect(self.search_files)
        self.search_bar.setFixedWidth(150)
        toolbar.addWidget(self.search_bar)

        self.sidebar = QListWidget()
        
        for icon, text in SIDEBAR_ITEMS:
            self.sidebar.addItem(QListWidgetItem(QIcon(f'{self.image_basepath}/sidebar/{icon}'), text))
        self.sidebar.clicked.connect(self.sidebar_item_clicked)

        self.init_favorites()
        self.add_new_tab()

    def init_favorites(self):
        self.sidebar_dock = QDockWidget("즐겨찾기", self)
        self.sidebar_dock.setWidget(self.sidebar)
        self.sidebar_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.sidebar_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        self.addDockWidget(Qt.RightDockWidgetArea, self.sidebar_dock)

        # sidebar_dock 크기 조절 및 숨김 기능 설정
        self.sidebar_dock.installEventFilter(self)
        self.sidebar_dock_hidden = False

    def init_footer(self):
        self.statusBar().showMessage("CopyRight 2024 @ Korea University AI Security Department")

    def eventFilter(self, obj, event):
        if obj == self.sidebar_dock and event.type() == QEvent.Resize:
            self.handle_sidebar_resize(event.size().width())
        return super().eventFilter(obj, event)

    def handle_sidebar_resize(self, width):
        if width < 100 and not self.sidebar_dock_hidden:
            self.sidebar_dock.hide()
            self.sidebar_dock_hidden = True

    def add_new_tab(self):
        new_tab = Tab_FileExplorer(self)
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

def main():
    app = QApplication(sys.argv)
    window = FileExplorer()
    window.show()
    sys.exit(app.exec_())