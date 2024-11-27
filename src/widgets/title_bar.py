from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QSizePolicy, QSpacerItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPalette, QColor

from enum import IntEnum, auto, Enum

from utils.load import load_stylesheet, image_base_path
from widgets.tabs import WidgetNewTab

class MaximizeButtonState(IntEnum):
    HOVER = auto()
    NORMAL = auto()

class MaximizeButtonIcon(str, Enum):
    RESTORE = "restore"
    MAXIMIZE = "maximize"

class WidgetTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.default_stylesheet = load_stylesheet("title_bar.css")
        self.background_color = "#BCD8EE"

        self.setFixedHeight(50)
        self.size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.init()

    def init(self):

        self.setContentsMargins(0, 0, 0, 0)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.addition_layouts()
        
        self.setLayout(self.main_layout)
        self.setStyleSheet(load_stylesheet("title_bar.css"))

    def addition_layouts(self):
        self.title_bar_layout()

        newtabs_layout = QHBoxLayout()
        self.newtab_widget = WidgetNewTab()

        newtabs_layout.addWidget(self.newtab_widget)
        self.main_layout.addLayout(newtabs_layout)

        newtab_add_layout : QHBoxLayout = self.newtab_add_button_layout()
        self.main_layout.addLayout(newtab_add_layout)

        controls_layout = self.window_control_layout()
        self.main_layout.addLayout(controls_layout)

    def title_bar_layout(self):
        palette = self.palette()
        palette.setColor(
            QPalette.Background, 
            QColor(self.background_color)
        )
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def newtab_add_button_layout(self):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)

        button = QPushButton()
        button.setObjectName("plus")
        button.setSizePolicy(self.size_policy)
        button.setIcon(QIcon(image_base_path("plus.png")))
        button.clicked.connect(self.EventTabAddition)

        layout.addWidget(button)

        return layout
    
    def EventTabAddition(self):
        self.newtab_widget.add_tab_widget("hello")

    def window_control_layout(self):

        self.CONTROLS_ICONS = {
            "MINIZE_BUTTON":"minimization.png",
            "NORMAL_BUTTON":"tabs.png",
            "MAXIMIZE_BUTTON":"maximization.png",
            "CLOSE_BUTTON":"close.png",
        }

        controls_layout = QHBoxLayout()
        controls_layout.setAlignment(Qt.AlignRight)
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        controls_layout.addItem(spacer)
        controls_layout.addStretch()

        for name, filename in self.CONTROLS_ICONS.items():
            if name == "NORMAL_BUTTON": continue
            
            self.__setattr__(name, QPushButton())

            button : QPushButton = getattr(self, name)
            button.setIcon(QIcon(image_base_path(filename)))
            button.setSizePolicy(self.size_policy)
            button.setObjectName(name)

            controls_layout.addWidget(button)

        self.MINIZE_BUTTON.clicked.connect(self.parent.showMinimized)
        self.CLOSE_BUTTON.clicked.connect(self.parent.close)
        self.MAXIMIZE_BUTTON.clicked.connect(self.maximize_button_event)

        self.MAXIMIZE_BUTTON.setState = self.maxmize_button_mouse_event

        return controls_layout

    def maxmize_button_mouse_event(self, state : MaximizeButtonState) -> None:
        if state == MaximizeButtonState.HOVER:
            self.MAXIMIZE_BUTTON.setStyleSheet("""
                QPushButton{
                    background: #caeeff;
                }
            """)
        elif state == MaximizeButtonState.NORMAL:
            self.MAXIMIZE_BUTTON.setStyleSheet("""
                QPushButton{
                    background: transparent;
                }
            """)

    def maximize_button_event(self) -> None:
        status = self.parent.isMaximized()

        if status:
            self.parent.showNormal()
            self.set_maximize_button_icon(MaximizeButtonIcon.MAXIMIZE)
        else:
            self.parent.showMaximized()
            self.set_maximize_button_icon(MaximizeButtonIcon.RESTORE)

    def set_maximize_button_icon(self, status : MaximizeButtonIcon) -> None:
        if status == MaximizeButtonIcon.MAXIMIZE:
            self.MAXIMIZE_BUTTON.setIcon(
                QIcon( image_base_path(self.CONTROLS_ICONS['MAXIMIZE_BUTTON']) )
            )
        elif status == MaximizeButtonIcon.RESTORE:
            self.MAXIMIZE_BUTTON.setIcon(
                QIcon( image_base_path(self.CONTROLS_ICONS['NORMAL_BUTTON']) )
            )

    def minimze_button_event(self) -> None:
        self.parent.showMinimized()