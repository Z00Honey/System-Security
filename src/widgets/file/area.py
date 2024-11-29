from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QSizePolicy
from widgets.file.file_list import FileList
from widgets.file.information import FileInformation
from widgets.file.search_list_widget import SearchListWidget


class FileArea(QWidget):
    """
    A widget containing a file list, search results, and file information.
    Handles switching between file list and search results.
    """
    def __init__(self, parent: QWidget = None, window: any = None, secure_manager: any = None) -> None:
        """
        Initializes the FileArea widget.

        Args:
            parent (QWidget): The parent widget.
            window (any): The main window object (optional).
            secure_manager (any): Object for managing secure folder access (optional).
        """
        super().__init__(parent)

        self.secure_manager = secure_manager  # Store secure manager object

        # Configure layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Initialize file list with secure_manager
        self.file_list = FileList(self, secure_manager=self.secure_manager)
        self.file_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.file_list, 1)

        # Add separator after file list
        self.separator_after_file_list = self.add_horizontal_separator()

        # Initialize search result widget
        self.search_result_list = SearchListWidget(self)
        self.search_result_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.search_result_list.hide()  # Initially hidden
        self.layout.addWidget(self.search_result_list, 1)

        # Add separator after search results
        self.separator_after_search_results = self.add_horizontal_separator()

        # Initialize file information widget
        self.file_info = FileInformation(self)
        self.file_info.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.layout.addWidget(self.file_info)

        self.setLayout(self.layout)

    def add_horizontal_separator(self) -> QFrame:
        """
        Adds a horizontal line separator to the layout.

        Returns:
            QFrame: The created line separator widget.
        """
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.HLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: black; margin: 0; padding: 0;")
        line_separator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.layout.addWidget(line_separator)
        return line_separator

    def get_status_search_results(self) -> bool:
        """
        Checks if the search result list is currently hidden.

        Returns:
            bool: True if the search result list is hidden, False otherwise.
        """
        return self.search_result_list.isHidden()

    def get_status_file_list(self) -> bool:
        """
        Checks if the file list is currently hidden.

        Returns:
            bool: True if the file list is hidden, False otherwise.
        """
        return self.file_list.isHidden()

    def show_search_results(self) -> None:
        """
        Displays the search result list and hides the file list and its separator.
        """
        # Hide file list and its separator
        self.file_list.hide()
        self.file_list.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.file_list.updateGeometry()
        self.separator_after_file_list.hide()

        # Show search result list
        self.search_result_list.show()
        self.search_result_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.search_result_list.updateGeometry()

        # Update layout
        self.layout.update()
        self.updateGeometry()

    def show_file_list(self) -> None:
        """
        Displays the file list and its separator, hiding the search result list.
        """
        # Hide search result list
        self.search_result_list.hide()
        self.search_result_list.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.search_result_list.updateGeometry()

        # Show file list and its separator
        self.separator_after_file_list.show()
        self.file_list.show()
        self.file_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.file_list.updateGeometry()

        # Update layout
        self.layout.update()
        self.updateGeometry()