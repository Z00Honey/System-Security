from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSizePolicy, QLabel
)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QIcon

from enum import IntEnum, auto

from utils.load import load_stylesheet, image_base_path


class TabWidgetState(IntEnum):
    """Enum for tab widget states."""
    HOVER = auto()
    NORMAL = auto()


class WidgetNewTab(QWidget):
    """
    Widget for managing new tabs with close buttons and hover effects.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        Initializes the WidgetNewTab.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.parent = parent
        self.tabs: list[QWidget] = []
        self.default_stylesheet: str = load_stylesheet("tabs.css")
        self.tab_mouse_event: TabWidgetState = TabWidgetState.NORMAL

        self.init_ui()

    def init_ui(self) -> None:
        """
        Sets up the UI components and layout.
        """
        self.setContentsMargins(0, 0, 0, 0)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.setState = self.set_state_hover_event  # Assigning the hover event handler
        self.setLayout(self.layout)

    def add_tab_widget(self, title: str) -> None:
        """
        Adds a new tab widget with a title and a close button.

        Args:
            title (str): The title of the new tab.
        """
        tab_widget = QWidget(self)
        tab_widget.setFixedSize(180, 50)

        self.add_title(tab_widget, title)
        self.add_tab_close_button(tab_widget)

        tab_widget.setObjectName("widget")
        tab_widget.setStyleSheet(self.default_stylesheet)

        self.tabs.append(tab_widget)
        self.layout.insertWidget(self.layout.count(), tab_widget)

    def add_title(self, tab_widget: QWidget, title: str) -> None:
        """
        Adds a title label to the tab widget.

        Args:
            tab_widget (QWidget): The tab widget to add the title to.
            title (str): The title text.
        """
        folder_icon = image_base_path("folder.png")
        tab_label = QLabel(
            (
                f'<img src="{folder_icon}" width="16" height="16" '
                f'style="vertical-align: middle;"> <span>{title}</span>'
            ),
            tab_widget
        )
        tab_label.setFixedSize(130, 40)
        tab_label.setAlignment(Qt.AlignCenter)
        tab_label.setObjectName('tabs')
        tab_label.move(10, 5)

        setattr(self, f"_tab{len(self.tabs) + 1}", tab_label)

    def add_tab_close_button(self, tab_widget: QWidget) -> None:
        """
        Adds a close button to the tab widget.

        Args:
            tab_widget (QWidget): The tab widget to add the close button to.
        """
        close_icon = QIcon(image_base_path("close.png"))
        close_button = QPushButton(tab_widget)
        close_button.setIcon(close_icon)
        close_button.setFixedSize(20, 20)
        close_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        close_button.clicked.connect(lambda: self.remove_tab(tab_widget))
        close_button.move(140, 15)

    def remove_tab(self, tab_widget: QWidget) -> None:
        """
        Removes a tab widget from the layout and deletes it.

        Args:
            tab_widget (QWidget): The tab widget to remove.
        """
        tab_to_remove = next(
            (x for x in self.tabs if x is tab_widget),
            None
        )

        if tab_to_remove:
            self.tabs.remove(tab_to_remove)
            self.layout.removeWidget(tab_widget)
            tab_widget.deleteLater()

    def set_state_hover_event(
        self, state: TabWidgetState, tab: QLabel = None
    ) -> None:
        """
        Handles hover state changes for tabs.

        Args:
            state (TabWidgetState): The new state (HOVER or NORMAL).
            tab (QLabel, optional): Specific tab label to apply the state to.
                If None, applies to all tabs. Defaults to None.
        """
        hover_stylesheet = load_stylesheet("tab_hover.css", True)
        normal_stylesheet = load_stylesheet("tab_normal.css", True)

        if state == TabWidgetState.HOVER:
            print("set HOVER")
            self.tab_mouse_event = TabWidgetState.HOVER
            if tab:
                tab.setStyleSheet(self.default_stylesheet + hover_stylesheet)
        elif state == TabWidgetState.NORMAL:
            print("set NORMAL")
            self.tab_mouse_event = TabWidgetState.NORMAL
            if tab:
                tab.setStyleSheet(self.default_stylesheet + normal_stylesheet)
            else:
                for tab_label in self.tabs:
                    tab_label.setStyleSheet(self.default_stylesheet + normal_stylesheet)