from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame, QMessageBox  # 수정: QMessageBox 임포트 추가
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path
import os


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

        # Create and add buttons
        self.home_button = self.create_button("home.png", "홈 디렉토리")
        self.pc_button = self.create_button("pc.png", "내 PC")
        self.layout.addWidget(self.home_button)
        self.layout.addWidget(self.pc_button)

        self.add_horizontal_separator()

        self.desktop_button = self.create_button("desktop.png", "바탕화면")
        self.documents_button = self.create_button("documents.png", "문서")
        self.downloads_button = self.create_button("downloads.png", "다운로드")
        self.layout.addWidget(self.desktop_button)
        self.layout.addWidget(self.documents_button)
        self.layout.addWidget(self.downloads_button)

        # Connect button click events
        self.home_button.clicked.connect(self.go_to_home)
        self.pc_button.clicked.connect(self.go_to_pc)
        self.desktop_button.clicked.connect(self.go_to_desktop)
        self.documents_button.clicked.connect(self.go_to_documents)
        self.downloads_button.clicked.connect(self.go_to_downloads)

        # Set layout and styles
        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("sidebar.css"))
        self.setObjectName("file_directory")

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

    # Directory navigation methods
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