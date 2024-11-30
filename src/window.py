from screeninfo import get_monitors
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QFrame
from PyQt5.QtGui import QShowEvent, QRegion, QPainterPath
from PyQt5.QtCore import Qt, QByteArray, QSize, QRectF, QEvent
from widgets.bar.title.title import WidgetTitleBar
from widgets.bar.address.address import AddressBar
from widgets.bar.tool import ToolBar
from widgets.bar.explorer.explorer import FileExplorerBar

from utils.native.util import setWindowNonResizable, isWindowResizable
from utils.load import load_stylesheet
from utils.native.native_event import _nativeEvent
from utils.secure import SecureFolderManager  # 보안 폴더 관리

# Global variable for current path
global GLOBAL_CURRENT_PATH
GLOBAL_CURRENT_PATH = ""


class MainWindow(QMainWindow):
    """Main window class for the File Explorer."""

    def __init__(self) -> None:
        """Initialize the main window and its components."""
        super().__init__()
        self.secure_manager = SecureFolderManager()  # Create security manager instance
        self.init_GUI()

    def init_GUI(self) -> None:
        """Initialize the GUI layout and settings."""
        self.setWindowTitle("FILE Explorer")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(*(self.auto_position()))
        self.setObjectName("main")

        # Set up central widget
        self.central_widget = QWidget()
        self.central_widget.setObjectName("central_widget")
        self.setCentralWidget(self.central_widget)

        # Set up layout
        self.layout: QVBoxLayout = QVBoxLayout(self.central_widget)
        self.init_layout()
        self.qss_load()

    def qss_load(self) -> None:
        """Load the main stylesheet."""
        self.setStyleSheet(load_stylesheet("main.css"))

    def init_layout(self) -> None:
        """Set up the layout for the main window."""
        # Add title bar
        self.title_bar = WidgetTitleBar(self)
        self.layout.addWidget(self.title_bar)
        self.add_horizontal_separator()

        # Add address bar
        self.address_bar = AddressBar(self, secure_manager=self.secure_manager)  # Pass security manager
        self.layout.addWidget(self.address_bar)
        self.add_horizontal_separator()

        # Add tool bar
        self.tool_bar = ToolBar(self, secure_manager=self.secure_manager)
        self.layout.addWidget(self.tool_bar)
        self.add_horizontal_separator()

        # Add file explorer bar
        self.file_explorer_bar = FileExplorerBar(self, secure_manager=self.secure_manager)  # Pass security manager
        self.layout.addWidget(self.file_explorer_bar, 1)

        # Set layout margins and spacing
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

    def auto_position(self) -> tuple[int, int, int, int]:
        """
        Automatically position the window at the center of the screen.

        Returns:
            tuple: A tuple containing x, y, width, and height.
        """
        display = get_monitors()[0]
        width = 1920
        height = 1080
        x = (display.width - width) // 2
        y = (display.height - height) // 2
        return (x, y if y else 100, width, height)

    def add_horizontal_separator(self) -> None:
        """Add a horizontal line separator to the layout."""
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.HLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: black;")
        self.layout.addWidget(line_separator)

    def setNonResizable(self) -> None:
        """Disable window resizing."""
        setWindowNonResizable(self.winId())
        self.title_bar.maximize_button.hide()

    def isResizable(self) -> bool:
        """Check if the window is resizable.

        Returns:
            bool: True if resizable, False otherwise.
        """
        return isWindowResizable(self.winId())

    def showEvent(self, event: QShowEvent) -> None:
        """Handle the show event."""
        self.title_bar.raise_()
        super(MainWindow, self).showEvent(event)

    def nativeEvent(self, event_type: QByteArray, message: int) -> tuple[int, int]:
        """Handle native events.

        Args:
            event_type (QByteArray): Type of the event.
            message (int): Message associated with the event.

        Returns:
            tuple: Processed event results.
        """
        return _nativeEvent(self, event_type, message)

    def resizeEvent(self, e) -> None:
        """Handle the resize event."""
        super().resizeEvent(e)
        self.title_bar.resize(self.width(), self.title_bar.height())

    def show_file_list(self) -> None:
        """Display the file list in the file explorer."""
        self.file_explorer_bar.file_area.show_file_list()

    def show_search_results(self) -> None:
        """Display the search results."""
        self.file_explorer_bar.file_area.show_search_results()

    def get_status_tree_view(self) -> int:
        """Get the current status of the tree view.

        Returns:
            int: Status of the tree view (0, 1, or 2).
        """
        search_status = self.file_explorer_bar.file_area.get_status_search_results()
        file_status = self.file_explorer_bar.file_area.get_status_file_list()

        if search_status != file_status:
            if search_status:
                return 1
            elif file_status:
                return 2
        return 0

    def search_result_addItem(self, path: str) -> None:
        """Add an item to the search results.

        Args:
            path (str): The path of the item to add.
        """
        result_items = self.file_explorer_bar.file_area.search_result_list
        result_items.add_item(path)

    def clear_search_result(self) -> None:
        """Clear all search results."""
        self.file_explorer_bar.file_area.search_result_list.clear()

    def file_event(self, mode: str) -> bool:
        """Handle file events like copy, cut, paste, or delete.

        Args:
            mode (str): The file operation mode.

        Returns:
            bool: True if the event was handled, False otherwise.
        """
        if mode == 'copy':
            self.file_explorer_bar.file_area.file_list.copySelectedFiles(cut=False)
        elif mode == 'cut':
            self.file_explorer_bar.file_area.file_list.copySelectedFiles(cut=True)
        elif mode == 'paste':
            self.file_explorer_bar.file_area.file_list.pasteFiles()
        elif mode == 'delete':
            self.file_explorer_bar.file_area.file_list.deleteSelectedFiles()
        else:
            return False
        return True
