from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from collections import defaultdict
from utils.load import image_base_path, load_stylesheet
import os


class FileInformation(QWidget):
    """Widget to display file or folder information."""

    def __init__(self, parent=None) -> None:
        """
        Initialize the FileInformation widget.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)

        # Header layout
        self.title_layout = QHBoxLayout()

        self.icon_label = QLabel(self)
        icon_path = image_base_path("file_information.png")
        self.icon_label.setPixmap(QPixmap(icon_path).scaled(24, 24))

        self.title_label = QLabel("파일 정보", self)

        self.title_layout.addWidget(self.icon_label)
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch()

        self.layout.addLayout(self.title_layout)
        self.add_horizontal_separator()

        # Info layout
        self.info_layout = QVBoxLayout()
        self.layout.addLayout(self.info_layout)

        # Apply stylesheet and object name
        self.setStyleSheet(load_stylesheet("file_information.css"))
        self.setObjectName("file_information")

        # Set default height and hide widget
        self.setFixedHeight(180)
        self.hide()

    def add_horizontal_separator(self) -> None:
        """Add a horizontal separator line."""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line)

    def get_folder_contents_count(self, folder_path: str) -> tuple[int, int]:
        """
        Get the number of files and folders inside a folder.

        Args:
            folder_path (str): Path to the folder.

        Returns:
            tuple[int, int]: Number of files and folders.
        """
        try:
            items = os.listdir(folder_path)
            file_count = len([item for item in items if os.path.isfile(os.path.join(folder_path, item))])
            folder_count = len([item for item in items if os.path.isdir(os.path.join(folder_path, item))])
            return file_count, folder_count
        except Exception:
            return 0, 0

    def get_file_types(self, folder_path: str) -> dict[str, int]:
        """
        Get the file types and their counts in a folder.

        Args:
            folder_path (str): Path to the folder.

        Returns:
            dict[str, int]: Dictionary of file extensions and their counts.
        """
        try:
            items = os.listdir(folder_path)
            file_types = defaultdict(int)

            for item in items:
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    _, ext = os.path.splitext(item)
                    if ext:
                        file_types[ext.upper()] += 1
            return dict(file_types)
        except Exception:
            return {}

    def show_file_info(self, file_info: dict[str, str]) -> None:
        """
        Display file or folder information.

        Args:
            file_info (dict[str, str]): Dictionary containing file or folder details.
        """
        # Clear existing information
        for i in reversed(range(self.info_layout.count())):
            self.info_layout.itemAt(i).widget().deleteLater()

        # Add new information
        for key, value in file_info.items():
            if key == "유형" and value == "폴더":
                # Folder-specific information
                info_label = QLabel(f"{key}: {value}")
                self.info_layout.addWidget(info_label)

                file_count, folder_count = self.get_folder_contents_count(file_info["경로"])
                contents_label = QLabel(f"포함된 항목: 파일 {file_count}개, 폴더 {folder_count}개")
                self.info_layout.addWidget(contents_label)
            else:
                # Generic information
                info_label = QLabel(f"{key}: {value}")
                self.info_layout.addWidget(info_label)

        self.show()

    def clear_info(self) -> None:
        """Clear displayed information and hide the widget."""
        self.hide()