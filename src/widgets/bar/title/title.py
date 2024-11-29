from PyQt5.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPalette, QColor

from enum import IntEnum, auto, Enum

from utils.load import load_stylesheet, image_base_path
from widgets.bar.title.tabs import WidgetNewTab


class MaximizeButtonState(IntEnum):
    """Enum for maximize button states."""
    HOVER = auto()
    NORMAL = auto()


class MaximizeButtonIcon(str, Enum):
    """Enum for maximize button icons."""
    RESTORE = "restore"
    MAXIMIZE = "maximize"


class WidgetTitleBar(QWidget):
    """Custom title bar widget for the main window."""

    def __init__(self, parent: QWidget = None) -> None:
        """
        Initializes the WidgetTitleBar.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.parent = parent

        self.default_stylesheet = load_stylesheet("title_bar.css")
        self.background_color = "#BCD8EE"

        self.setFixedHeight(50)
        self.size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.initialize()

    def initialize(self) -> None:
        """Sets up the title bar UI components."""
        self.setContentsMargins(0, 0, 0, 0)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.add_layouts()

        self.setLayout(self.main_layout)
        self.setStyleSheet(load_stylesheet("title_bar.css"))

    def add_layouts(self) -> None:
        """Adds the necessary layouts to the title bar."""
        self.setup_title_bar_layout()

        new_tabs_layout = QHBoxLayout()
        self.new_tab_widget = WidgetNewTab()

        new_tabs_layout.addWidget(self.new_tab_widget)
        self.main_layout.addLayout(new_tabs_layout)

        new_tab_add_layout = self.create_new_tab_button_layout()
        self.main_layout.addLayout(new_tab_add_layout)

        controls_layout = self.create_window_control_layout()
        self.main_layout.addLayout(controls_layout)

    def setup_title_bar_layout(self) -> None:
        """Configures the title bar's appearance."""
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(self.background_color))  # 수정 제안: QPalette.Background는 deprecated되었습니다.
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def create_new_tab_button_layout(self) -> QHBoxLayout:
        """
        Creates the layout for the 'Add New Tab' button.

        Returns:
            QHBoxLayout: The layout containing the add new tab button.
        """
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)

        button = QPushButton()
        button.setObjectName("plus")
        button.setSizePolicy(self.size_policy)
        button.setIcon(QIcon(image_base_path("plus.png")))
        button.clicked.connect(self.event_tab_addition)

        layout.addWidget(button)

        return layout

    def event_tab_addition(self) -> None:
        """Event handler for adding a new tab."""
        self.new_tab_widget.add_tab_widget("hello")

    def create_window_control_layout(self) -> QHBoxLayout:
        """
        Creates the layout for window control buttons.

        Returns:
            QHBoxLayout: The layout containing window control buttons.
        """
        self.CONTROLS_ICONS = {
            "MINIMIZE_BUTTON": "minimization.png",
            "NORMAL_BUTTON": "tabs.png",
            "MAXIMIZE_BUTTON": "maximization.png",
            "CLOSE_BUTTON": "close.png",
        }

        controls_layout = QHBoxLayout()
        controls_layout.setAlignment(Qt.AlignRight)
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        controls_layout.addItem(spacer)
        controls_layout.addStretch()

        for name, filename in self.CONTROLS_ICONS.items():
            if name == "NORMAL_BUTTON":
                continue

            setattr(self, name, QPushButton())

            button: QPushButton = getattr(self, name)
            button.setIcon(QIcon(image_base_path(filename)))
            button.setSizePolicy(self.size_policy)
            button.setObjectName(name)

            controls_layout.addWidget(button)

        self.MINIMIZE_BUTTON.clicked.connect(self.parent.showMinimized)
        self.CLOSE_BUTTON.clicked.connect(self.parent.close)
        self.MAXIMIZE_BUTTON.clicked.connect(self.maximize_button_event)

        self.MAXIMIZE_BUTTON.setState = self.maximize_button_mouse_event  # 비표준 방식이지만 기존 코드 유지

        return controls_layout

    def maximize_button_mouse_event(self, state: MaximizeButtonState) -> None:
        """
        Changes the maximize button's appearance based on mouse events.

        Args:
            state (MaximizeButtonState): The current state of the maximize button.
        """
        if state == MaximizeButtonState.HOVER:
            self.MAXIMIZE_BUTTON.setStyleSheet("""
                QPushButton {
                    background: #82bdea;
                }
            """)
        elif state == MaximizeButtonState.NORMAL:
            self.MAXIMIZE_BUTTON.setStyleSheet("""
                QPushButton {
                    background: transparent;
                }
            """)

    def maximize_button_event(self) -> None:
        """Toggles the window between maximized and normal states."""
        status = self.parent.isMaximized()

        if status:
            self.parent.showNormal()
            self.set_maximize_button_icon(MaximizeButtonIcon.MAXIMIZE)
        else:
            self.parent.showMaximized()
            self.set_maximize_button_icon(MaximizeButtonIcon.RESTORE)

    def set_maximize_button_icon(self, status: MaximizeButtonIcon) -> None:
        """
        Sets the icon for the maximize button based on window state.

        Args:
            status (MaximizeButtonIcon): The desired icon state.
        """
        if status == MaximizeButtonIcon.MAXIMIZE:
            self.MAXIMIZE_BUTTON.setIcon(
                QIcon(image_base_path(self.CONTROLS_ICONS['MAXIMIZE_BUTTON']))
            )
        elif status == MaximizeButtonIcon.RESTORE:
            self.MAXIMIZE_BUTTON.setIcon(
                QIcon(image_base_path(self.CONTROLS_ICONS['NORMAL_BUTTON']))
            )

    def minimize_button_event(self) -> None:
        """Minimizes the parent window."""
        self.parent.showMinimized()