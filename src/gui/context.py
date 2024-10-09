from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeView, QListWidget, QVBoxLayout, QWidget, QToolBar, QAction, QLineEdit, QHBoxLayout, QListWidgetItem,
    QTabWidget, QFileSystemModel, QMessageBox, QSplitter, QDockWidget, QHeaderView, QMenu, QActionGroup, QTabBar, QInputDialog
)
from PyQt5.QtCore import QDir, Qt, QSortFilterProxyModel, QEvent
from PyQt5.QtGui import QIcon

from .tabs.FileExplorer import Tab_FileExplorer
from .icons import SIDEBAR_ITEMS
#############################################↓↓↓
from secure_folder_manager import SecureFolderManager  #보안 폴더 매니저 모듈 가져오기
#############################################↑↑↑

import os
import sys

#<커스텀 탭바>
class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setElideMode(Qt.ElideRight)   #텍스트가 길면 오른쪽부터 생략

#<메인 윈도우 클래스>: 파일 탐색기의 메인 UI 정의
class FileExplorer(QMainWindow):
    def __init__(self):

        self.image_basepath = "./icon"

        super().__init__()
        ###########################################↓↓↓
         self.secure_manager = SecureFolderManager()  # 보안 폴더 관리자 초기화
        ###########################################↑↑↑
        self.SettingUserInterface()   #"사용자 인터페이스 설정 메소드"호출 (메인 UI 설정)↓↓

    #"사용자 인터페이스 설정 메소드"↑↑
    def SettingUserInterface(self):
        self.setWindowTitle("[일만집중하조] 파일 탐색기")
        self.setGeometry(100, 100, 1000, 700)

        os.chdir(os.path.dirname(os.path.abspath(__file__)))  #????

        #툴바 설정
        toolbar = QToolBar("메인 도구 모음")  #툴바 생성
        self.addToolBar(Qt.TopToolBarArea, toolbar)   #툴바 상단에 배치
        toolbar.setMovable(False)   #위치 고정   
        
        #탭위젯 설정
        self.tab_widget = QTabWidget()   #탭위젯 생성
        self.tab_widget.setTabBar(CustomTabBar())   #탭위젯을 <커스텀 탭바>로 지정
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tab_widget)

        #툴바에 추가할 액션 설정
        actions = [
            ('new.png', '새 탭', self.add_new_tab),
            ('back.png', '뒤로', self.go_back),
            ('front.png', '앞으로', self.go_forward),
            ('leftup.png', '상위 폴더', self.go_up)
        ]

        #각 액션들 툴바에 추가
        for icon, text, func in actions:
            action = QAction(QIcon(f'{self.image_basepath}/tab/{icon}'), text, self)
            action.triggered.connect(func)
            toolbar.addAction(action)

        #검색창 설정
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("파일 검색")
        self.search_bar.returnPressed.connect(self.search_files)
        self.search_bar.setFixedWidth(150)
        toolbar.addWidget(self.search_bar)

        #사이드바 설정
        self.sidebar = QListWidget()
        for icon, text in SIDEBAR_ITEMS:
            self.sidebar.addItem(QListWidgetItem(QIcon(f'{self.image_basepath}/sidebar/{icon}'), text))
        self.sidebar.clicked.connect(self.sidebar_item_clicked)

        # "즐겨찾기 초기화 메소드" 호출
        self.init_favorites()

         # "새 탭 추가 메소드" 호출
        self.add_new_tab()

    #"즐겨찾기 메소드"
    def init_favorites(self):
        self.sidebar_dock = QDockWidget("즐겨찾기", self)
        self.sidebar_dock.setWidget(self.sidebar)
        self.sidebar_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.sidebar_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        self.addDockWidget(Qt.RightDockWidgetArea, self.sidebar_dock)

        # sidebar_dock 크기 조절 및 숨김 기능 설정
        self.sidebar_dock.installEventFilter(self)
        self.sidebar_dock_hidden = False

    #"상태 표시줄 초기화 메소드"
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

    #"탭 추가 메소드"
    def add_new_tab(self):
        new_tab = Tab_FileExplorer(self)
        index = self.tab_widget.addTab(new_tab, "새 탭")
        self.tab_widget.setCurrentIndex(index)
        new_tab.navigate_to(QDir.homePath())

    #"탭을 닫는 메소드"
    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            self.close()

    # 사이드바 항목 클릭 시 호출되는 함수(사이드바에 즐겨찾기가 있는걸로 알고있는데..)
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

    #"이전 페이지 메소드"
    def go_back(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab.current_index > 0:
            current_tab.current_index -= 1
            current_tab.navigate_to(current_tab.history[current_tab.current_index])
    #"이후 페이지 메소드"
    def go_forward(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab.current_index < len(current_tab.history) - 1:
            current_tab.current_index += 1
            current_tab.navigate_to(current_tab.history[current_tab.current_index])

    #"상위 폴더 메소드"
    def go_up(self):
        current_tab = self.tab_widget.currentWidget()
        current_path = current_tab.address_bar.text()
        parent_path = os.path.dirname(current_path)
        current_tab.navigate_to(parent_path)

    #파일검색기능
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

#프로그램 진입점
def main():
    app = QApplication(sys.argv)  
    window = FileExplorer()  #<메인 윈도우 클래스>  생성
    ####################################↓↓↓
    window.secure_manager.set_initial_password(window)  # 초기 비밀번호 설정 (최초 실행 시)
    ####################################↑↑↑
    window.show()
    sys.exit(app.exec_())
