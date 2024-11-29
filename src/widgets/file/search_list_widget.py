import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication,
    QTreeView,
    QAbstractItemView,
    QWidget,
    QVBoxLayout,
    QHeaderView,
    QFileIconProvider,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal, QFileInfo
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class SearchListWidget(QWidget):
    """Custom widget for displaying a searchable list of files and folders."""
    path_changed = pyqtSignal(str)  # Signal emitted when the path changes

    def __init__(self, parent=None) -> None:
        """
        Initialize the SearchListWidget.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.tree_view = QTreeView(self)
        self.tree_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setup_ui()
        self.setup_model()

        self.layout.addWidget(self.tree_view)
        self.setLayout(self.layout)

        # Connect item click event
        self.tree_view.clicked.connect(self.on_item_clicked)

    def setup_ui(self) -> None:
        """Set up the UI properties of the tree view."""
        self.tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree_view.setDragEnabled(True)
        self.tree_view.setAcceptDrops(False)
        self.tree_view.setDropIndicatorShown(False)
        self.tree_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = self.tree_view.header()
        header.setStretchLastSection(True)
        header.setSectionsMovable(True)

        self.tree_view.setRootIsDecorated(False)
        self.tree_view.setItemsExpandable(False)
        self.tree_view.setAlternatingRowColors(True)

        # Set custom styles
        self.tree_view.setStyleSheet("""
            QTreeView::item { 
                height: 35px;
                padding: 5px;
            }
        """)

    def setup_model(self) -> None:
        """Set up the data model for the tree view."""
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Name", "Date Modified", "Type", "Size"])
        self.tree_view.setModel(self.model)

        # Configure column sizes
        header = self.tree_view.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)

        self.tree_view.setColumnWidth(0, 300)  # Name
        self.tree_view.setColumnWidth(1, 150)  # Date Modified
        self.tree_view.setColumnWidth(2, 100)  # Type
        self.tree_view.setColumnWidth(3, 100)  # Size

    def set_paths(self, paths: list[str]) -> None:
        """
        Load a list of file and folder paths into the model.

        Args:
            paths (list[str]): List of file or folder paths.
        """
        self.model.removeRows(0, self.model.rowCount())  # Clear existing items

        for path in paths:
            if os.path.exists(path):
                self.add_item(path)
            else:
                # Handle invalid paths
                name_item = QStandardItem(os.path.basename(path))
                name_item.setForeground(Qt.red)
                date_item = QStandardItem("N/A")
                type_item = QStandardItem("Invalid Path")
                size_item = QStandardItem("N/A")
                for item in [name_item, date_item, type_item, size_item]:
                    item.setEditable(False)
                self.model.appendRow([name_item, date_item, type_item, size_item])

    def add_item(self, path: str) -> None:
        """
        Add a file or folder to the model with its details.

        Args:
            path (str): Path of the file or folder.
        """
        name = os.path.basename(path)
        name_item = QStandardItem(name)
        name_item.setData(path, Qt.UserRole)  # Store file path as data

        last_modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")
        date_item = QStandardItem(last_modified)

        icon_provider = QFileIconProvider()
        file_info = QFileInfo(path)
        icon = icon_provider.icon(file_info)

        if os.path.isdir(path):
            type_str = "Folder"
            size_str = "-"
        else:
            ext = os.path.splitext(path)[1][1:].upper()
            type_str = f"{ext} File" if ext else "File"
            size_str = self.human_readable_size(os.path.getsize(path))

        type_item = QStandardItem(type_str)
        size_item = QStandardItem(size_str)

        name_item.setIcon(icon)

        for item in [name_item, date_item, type_item, size_item]:
            item.setEditable(False)

        self.model.appendRow([name_item, date_item, type_item, size_item])

    def on_item_clicked(self, index) -> None:
        """
        Handle item click event to display file details.

        Args:
            index: Index of the clicked item.
        """
        index = index.sibling(index.row(), 0)
        item = self.model.itemFromIndex(index)
        if item:
            file_path = item.data(Qt.UserRole)
            self.show_file_info(file_path)

    def show_file_info(self, file_path: str) -> None:
        """
        Display detailed information about a file or folder.

        Args:
            file_path (str): Path of the file or folder.
        """
        if os.path.exists(file_path):
            name = os.path.basename(file_path)
            if os.path.isdir(file_path):
                file_type = "Folder"
                size = "Folder"
            else:
                ext = os.path.splitext(file_path)[1][1:].upper()
                file_type = f"{ext} File" if ext else "File"
                size = self.human_readable_size(os.path.getsize(file_path))

            last_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")

            file_info = {
                "Name": name,
                "Path": file_path,
                "Type": file_type,
                "Last Modified": last_modified,
                "Size": size,
            }
        else:
            file_info = {
                "Name": "Unknown",
                "Path": file_path,
                "Type": "Unknown",
                "Last Modified": "Unknown",
                "Size": "Unknown",
            }

        file_area = self.parent()
        while file_area and not hasattr(file_area, 'file_info'):
            file_area = file_area.parent()
        if file_area and hasattr(file_area, 'file_info'):
            file_area.file_info.show_file_info(file_info)

    @staticmethod
    def human_readable_size(size: int) -> str:
        """
        Convert size in bytes to a human-readable format.

        Args:
            size (int): Size in bytes.

        Returns:
            str: Human-readable size string.
        """
        for unit in ["Bytes", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    def clear(self) -> None:
        """Clear the tree view model."""
        self.tree_view.model().clear()
        self.tree_view.model().setHorizontalHeaderLabels(["Name", "Date Modified", "Type", "Size"])