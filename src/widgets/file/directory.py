from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame, QMessageBox, QMenu, QInputDialog, QLineEdit  # QLineEdit 추가
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
from utils.load import load_stylesheet, image_base_path
import os
import pickle


class FileDirectory(QWidget):
    """
    Sidebar widget for navigating file directories.
    """
    def __init__(self, parent: QWidget = None, secure_manager: any = None) -> None:
        """
        Initializes the FileDirectory widget.

        Args:
            parent (QWidget): The parent widget.
            secure_manager (any): Object managing secure folder access.
        """
        super().__init__(parent)
        self.secure_manager = secure_manager  # Store secure manager object

        # Configure layout
        self.layout = QVBoxLayout()
        self.setFixedWidth(225)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)


        # 기본 즐겨찾기 버튼들
        self.default_bookmarks = {
            "home": ("home.png", "홈 디렉토리", os.path.expanduser("~")),
            "pc": ("pc.png", "내 PC", "C:\\"),
            "desktop": ("desktop.png", "바탕화면", os.path.join(os.path.expanduser("~"), "Desktop")),
            "documents": ("documents.png", "문서", os.path.join(os.path.expanduser("~"), "Documents")),
            "downloads": ("downloads.png", "다운로드", os.path.join(os.path.expanduser("~"), "Downloads"))
        }

        self.bookmark_buttons = []
        self.add_default_bookmarks()

        # right click menu
        #self.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.customContextMenuRequested.connect(self.show_main_context_menu)

        self.empty_space = QWidget()
        self.empty_space.setContextMenuPolicy(Qt.CustomContextMenu)
        self.empty_space.customContextMenuRequested.connect(self.show_main_context_menu)
        self.layout.addWidget(self.empty_space)

        self.bookmark_file = "utils\\setting\\fav.bin"
        self.load_bookmarks()
        self.layout.addStretch()

        # Set layout and styles
        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("sidebar.css"))
        self.setObjectName("file_directory")

        self.empty_space.setStyleSheet("background: transparent;")
        self.empty_space.setMinimumHeight(50)  # 적절한 높이 설정

    def create_button(self, icon_name: str, tooltip: str) -> QPushButton:
        """
        Creates a styled button for the sidebar.

        Args:
            icon_name (str): The filename of the button's icon.
            tooltip (str): Tooltip text for the button.

        Returns:
            QPushButton: The created button.
        """
        button = QPushButton()
        icon_path = image_base_path(icon_name)
        button.setIcon(QIcon(icon_path))
        button.setToolTip(tooltip)
        button.setText(tooltip)
        button.setIconSize(QSize(24, 24))
        button.setStyleSheet("text-align: left; padding-left: 10px;")
        button.setFixedSize(225, 40)
        return button

    def add_horizontal_separator(self) -> None:
        """
        Adds a horizontal line separator to the layout.
        """
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.HLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: rgba(0, 0, 0, 0.5); margin: 10px 0;")
        self.layout.addWidget(line_separator)

    def get_main_window(self) -> QWidget:
        """
        Retrieves the main window by traversing the parent hierarchy.

        Returns:
            QWidget: The main window, or None if not found.
        """
        parent = self.parent()
        while parent is not None:
            if type(parent).__name__ == 'MainWindow':
                return parent
            parent = parent.parent()
        return None

    def get_file_list(self) -> QWidget:
        """
        Retrieves the file list widget from the main window.

        Returns:
            QWidget: The file list widget, or None if not found.
        """
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'file_explorer_bar'):
            return main_window.file_explorer_bar.file_area.file_list
        return None

    def get_navigation_widget(self) -> QWidget:
        """
        Retrieves the navigation widget from the address bar.

        Returns:
            QWidget: The navigation widget, or None if not found.
        """
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'address_bar'):
            return main_window.address_bar.navigation_widget
        return None

    def navigate_to(self, path: str) -> None:
        """
        Navigates to the specified path, with secure folder checks.

        Args:
            path (str): The target path to navigate to.
        """
        secure_folder_path = os.path.normpath(self.secure_manager.secure_folder_path) if self.secure_manager else None
        current_path = os.path.normpath(path)

        # Authenticate for secure folder access
        if secure_folder_path and secure_folder_path in current_path and not self.secure_manager.authenticated:
            self.secure_manager.authenticate()
            if not self.secure_manager.authenticated:
                return  # Abort if authentication fails

        # De-authenticate when leaving the secure folder
        if self.secure_manager and self.secure_manager.authenticated and secure_folder_path not in current_path:
            self.secure_manager.authenticated = False
            QMessageBox.information(self, "De-authenticated", "You have exited the secure folder. Authentication has been cleared.")
            

        # Update file list and navigation history
        file_list = self.get_file_list()
        nav_widget = self.get_navigation_widget()
        if file_list and nav_widget:
            nav_widget.add_to_history(path)
            file_list.set_current_path(path)

    def go_to_home(self) -> None:
        """Navigates to the home directory."""
        self.navigate_to(os.path.expanduser("~"))

    def go_to_pc(self) -> None:
        """Navigates to the root of the C drive."""
        self.navigate_to("C:\\")

    def go_to_desktop(self) -> None:
        """Navigates to the desktop directory."""
        self.navigate_to(os.path.join(os.path.expanduser("~"), "Desktop"))

    def go_to_documents(self) -> None:
        """Navigates to the documents directory."""
        self.navigate_to(os.path.join(os.path.expanduser("~"), "Documents"))

    def go_to_downloads(self) -> None:
        """Navigates to the downloads directory."""
        self.navigate_to(os.path.join(os.path.expanduser("~"), "Downloads"))

    def go_to_secure_folder(self) -> None:
        """Navigates to the secure folder."""
        self.navigate_to(self.secure_manager.secure_folder_path)
            
    def reset(self) -> None:
        """
        Resets the secure folder password manager.

        If authenticated, the password is cleared. Otherwise, a warning is shown.
        """
        if self.secure_manager and self.secure_manager.authenticated:
            self.secure_manager.pwd_mgr.reset()
            # QMessageBox.information(self, "Reset Complete", "Password has been reset.")  # Optional success message
        else:
            QMessageBox.warning(self, "Secure Folder Access", "Please access the secure folder first.")
            self.go_to_secure_folder()


    def add_default_bookmarks(self):
        """기본 즐겨찾기 버튼들을 추가합니다."""
        # 먼저 홈과 PC 버튼 추가
        for key in ["home", "pc"]:
            data = self.default_bookmarks[key]
            button = self.create_bookmark_button(data[0], data[1], data[2])
            self.layout.addWidget(button)
            self.bookmark_buttons.append(button)

        # PC와 Desktop 사이에 구분선 추가
        self.add_horizontal_separator()

        # 나머지 버튼들 추가 (desktop, documents, downloads)
        for key in ["desktop", "documents", "downloads"]:
            data = self.default_bookmarks[key]
            button = self.create_bookmark_button(data[0], data[1], data[2])
            self.layout.addWidget(button)
            self.bookmark_buttons.append(button)

    def create_bookmark_button(self, icon_name: str, tooltip: str, path: str) -> QPushButton:
        """즐겨찾기 버튼을 생성합니다."""
        button = self.create_button(icon_name, tooltip)
        button.clicked.connect(lambda: self.navigate_to(path))
        button.setProperty("path", path)
        button.setContextMenuPolicy(Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(
            lambda pos, b=button: self.show_bookmark_context_menu(pos, b)
        )
        
        # 더블클릭 이벤트 처리를 위한 편집 모드 속성 추가
        button.is_editing = False
        button.mouseDoubleClickEvent = lambda event, b=button: self.start_inline_edit(b)
        
        return button

    def start_inline_edit(self, button):
        """버튼의 인라인 편집을 시작합니다."""
        if button not in self.bookmark_buttons:  # 기본 즐겨찾기는 편집 불가
            return
        
        if not button.is_editing:
            button.is_editing = True
            text = button.text()
            button.setVisible(False)
            
            # 인라인 편집을 위한 QLineEdit 생성
            edit = QLineEdit(text, self)
            edit.setFixedSize(button.size())
            edit.setStyleSheet(button.styleSheet())
            self.layout.replaceWidget(button, edit)
            
            def finish_editing():
                if edit.text().strip():  # 빈 문자열이 아닌 경우에만 적용
                    button.setText(edit.text())
                    button.setToolTip(edit.text())
                button.is_editing = False
                button.setVisible(True)
                self.layout.replaceWidget(edit, button)
                edit.deleteLater()
            
            # Enter 키나 포커스를 잃었을 때 편집 완료
            edit.returnPressed.connect(finish_editing)
            edit.focusOutEvent = lambda e: finish_editing()
            
            edit.selectAll()
            edit.setFocus()

    def show_main_context_menu(self, pos):
        """빈 공간 우클릭 메뉴를 표시합니다."""
        file_list = self.get_file_list()
        if not file_list:
            return

        context_menu = QMenu(self)
        add_bookmark_action = context_menu.addAction("현재 위치를 즐겨찾기에 추가")
        
        action = context_menu.exec_(self.mapToGlobal(pos))
        if action == add_bookmark_action:
            self.add_bookmark(file_list.get_current_path())

    def show_bookmark_context_menu(self, pos, button):
        """즐겨찾기 버튼의 우클릭 메뉴를 표시합니다."""
        context_menu = QMenu(self)
        button_path = button.property("path")
        
        # PC와 홈 버튼 여부 확인
        is_above_separator = (button_path == self.default_bookmarks["pc"][2] or 
                            button_path == self.default_bookmarks["home"][2])
        
        # separator 아래에 있는 버튼들에만 즐겨찾기 추가 메뉴 표시
        if not is_above_separator:
            add_bookmark_action = context_menu.addAction("현재 위치를 즐겨찾기에 추가")
        
        # PC와 홈 버튼이 아닌 경우에만 삭제와 이름 변경 메뉴 추가
        if not is_above_separator:
            remove_action = context_menu.addAction("즐겨찾기 제거")
            rename_action = context_menu.addAction("즐겨찾기 이름변경(우클릭)")
        
        action = context_menu.exec_(button.mapToGlobal(pos))
        if not is_above_separator:
            if action == remove_action:
                self.remove_bookmark(button)
            elif action == rename_action:
                self.start_inline_edit(button)
            elif 'add_bookmark_action' in locals() and action == add_bookmark_action:
                file_list = self.get_file_list()
                if file_list:
                    self.add_bookmark(file_list.get_current_path())

    def add_bookmark(self, path: str):
        """새로운 즐겨찾기를 추가합니다."""
        name = os.path.basename(path)
        button = self.create_bookmark_button("folder.png", name, path)
        
        # 레이아웃에서 downloads 버튼의 실제 인덱스를 찾습니다
        downloads_layout_index = -1
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.property("path") == self.default_bookmarks["downloads"][2]:
                downloads_layout_index = i
                break
        
        if downloads_layout_index != -1:
            # downloads 버튼 바로 다음에 새 버튼 삽입
            self.layout.insertWidget(downloads_layout_index + 1, button)
        else:
            # downloads 버튼을 찾지 못한 경우 마지막에 추가 (stretch 전)
            self.layout.insertWidget(self.layout.count() - 1, button)
        
        self.bookmark_buttons.append(button)
        self.save_bookmarks()  # 즐겨찾기 추가 후 저장

    def remove_bookmark(self, button):
        """즐겨찾기를 제거합니다."""
        self.layout.removeWidget(button)
        self.bookmark_buttons.remove(button)
        button.deleteLater()
        self.save_bookmarks()  # 즐겨찾기 제거 후 저장

    def save_bookmarks(self):
        """사용자가 추가한 즐겨찾기를 파일에 저장합니다."""
        bookmarks = []
        for button in self.bookmark_buttons:
            path = button.property("path")
            # default_bookmarks에 없는 버튼만 저장
            if not any(path == bookmark[2] for bookmark in self.default_bookmarks.values()):
                bookmarks.append({
                    'name': button.text(),
                    'path': path
                })
        
        try:
            with open(self.bookmark_file, 'wb') as f:
                pickle.dump(bookmarks, f)
        except Exception as e:
            print(f"즐겨찾기 저장 중 오류 발생: {e}")

    def load_bookmarks(self):
        """저장된 즐겨찾기를 불러옵니다."""
        try:
            if os.path.exists(self.bookmark_file):
                with open(self.bookmark_file, 'rb') as f:
                    bookmarks = pickle.load(f)
                    for bookmark in bookmarks:
                        button = self.create_bookmark_button(
                            "folder.png", 
                            bookmark['name'], 
                            bookmark['path']
                        )
                        self.layout.insertWidget(self.layout.count() - 1, button)
                        self.bookmark_buttons.append(button)
        except Exception as e:
            print(f"즐겨찾기 불러오기 중 오류 발생: {e}")