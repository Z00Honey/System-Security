from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy, QLabel
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QIcon, QColor

from enum import IntEnum, auto

from utils.load import load_stylesheet, image_base_path

class TabWidgetState(IntEnum):
    HOVER = auto()
    NORMAL = auto()

class WidgetNewTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.tabs = []
        self.init()

        self.default_stylesheet = load_stylesheet("tabs.css")

    def init(self):
        self.setContentsMargins(0, 0, 0, 0)
        
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.setState = self.SetStateHoverEvent
        self.tab_mouse_event = TabWidgetState.NORMAL

        self.setLayout(self.layout)

    def add_tab_widget(self, title) -> None:

        tab_widget = QWidget(self)
        tab_widget.setFixedSize(180, 50)

        self.add_title(tab_widget, title)
        self.add_tab_close_button(tab_widget)

        tab_widget.setObjectName("widget")
        tab_widget.setStyleSheet(self.default_stylesheet)

        self.tabs.append(tab_widget)

        self.layout.insertWidget(self.layout.count(), tab_widget)
    
    def add_title(self, tab_widget, title):
        folder_icon = image_base_path("folder.png")

        tab_label = QLabel(f'<img src="{folder_icon}" width="16" height="16" style="vertical-align: middle;"> <span>{title}</span>', tab_widget)
        tab_label.setFixedSize(130, 40)
        tab_label.setAlignment(Qt.AlignCenter)
        tab_label.setObjectName('tabs')
        tab_label.move(10, 5)

        setattr(self, f"_tab{len(self.tabs)+1}", tab_label)

    def add_tab_close_button(self, tab_widget):
        close_icon = QIcon(image_base_path("close.png"))

        close_button = QPushButton(tab_widget)

        close_button.setIcon(close_icon)
        close_button.setFixedSize(20, 20)
        close_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        close_button.clicked.connect(lambda: self.remove_tab(tab_widget))

        close_button.move(140, 15)

    def remove_tab(self, tab_widget):
        tab_to_remove = filter(
            (lambda x: x is tab_widget),
            self.tabs
        ).__next__()

        if tab_to_remove:
            self.tabs.remove(tab_to_remove)
            self.layout.removeWidget(tab_widget)
            tab_widget.deleteLater()

    # def eventFilter(self, source, event):

    #     if event.type() == QEvent.Enter:
    #         if source in self.tabs:
    #             self.SetStateHoverEvent(TabWidgetState.HOVER, source)

    #     elif event.type() == QEvent.Leave:
    #         print("QEvent.Leave", self.tab_mouse_event == TabWidgetState.HOVER)
    #         if self.tab_mouse_event == TabWidgetState.HOVER:
    #             return super().eventFilter(source, event)
    #         elif source in self.tabs:
    #             self.SetStateHoverEvent(TabWidgetState.NORMAL, source)

    #     return super().eventFilter(source, event)

    def SetStateHoverEvent(self, state : TabWidgetState, tab : QLabel = None):
        hover_stylesheet = load_stylesheet("tab_hover.css", True)
        normal_stylesheet = load_stylesheet("tab_normal.css", True)

        if state == TabWidgetState.HOVER:
            print("set HOVER")
            self.tab_mouse_event = TabWidgetState.HOVER
            tab.setStyleSheet(self.default_stylesheet + hover_stylesheet)
        elif state == TabWidgetState.NORMAL:
            print("set NORMAL")
            self.tab_mouse_event = TabWidgetState.NORMAL
            if not tab:
                for tab_label in self.tabs:
                    tab_label.setStyleSheet(self.default_stylesheet + normal_stylesheet)
            else:
                tab.setStyleSheet(self.default_stylesheet + normal_stylesheet)