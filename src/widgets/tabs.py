from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor

from enum import IntEnum, auto

from utils.load import load_stylesheet, image_base_path

class LabelEventState(IntEnum):
    HOVER = auto()
    NORMAL = auto()

class WidgetNewTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.tabs = []
        self.init()

        self.add_tab_widget("File Explorer 1")
        self.add_tab_widget("File Explorer 2")

    def init(self):
        self.setContentsMargins(0, 0, 0, 0)
        
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setState = self.SetStateHoverEvent

        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("tabs.css"))

    def add_tab_widget(self, title) -> None:
        icon_path = image_base_path("folder.png")

        tab = QLabel(f'<img src="{icon_path}" width="16" height="16"> <span>{title}</span>', self)

        tab.setAlignment(Qt.AlignCenter)
        tab.setFixedWidth(150)
        tab.setObjectName('tabs')

        setattr(self, f"_tab{len(self.tabs)+1}", tab)

        self.tabs.append(tab)
        self.layout.addWidget(tab)


    def SetStateHoverEvent(self, state : LabelEventState, tab : QLabel = None):
        if state == LabelEventState.HOVER:
            tab.setStyleSheet(load_stylesheet("NewTabsHover.css", True))
        elif state == LabelEventState.NORMAL:
            if not tab:
                for i in self.tabs:
                    i.setStyleSheet(load_stylesheet("NewTabsNormal.css", True))
            else:
                tab.setStyleSheet(load_stylesheet("NewTabsNormal.css", True))