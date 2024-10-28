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

        self.background_color = "#d9f3ff"
        
        self.setFixedHeight(80)
        self.size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.init()

    def init(self):
        self.setContentsMargins(0, 0, 0, 0)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.addition_layouts()
        
        self.setLayout(self.main_layout)
        self.setStyleSheet(load_stylesheet("title_bar.css"))

    def addition_layouts(self):
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        self.newtab_widget = WidgetNewTab()
        top_layout.addWidget(self.newtab_widget)

        newtab_add_layout = self.newtab_add_button_layout()
        top_layout.addLayout(newtab_add_layout)

        controls_layout = self.window_control_layout()
        top_layout.addLayout(controls_layout)

        self.main_layout.addLayout(top_layout)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)


        extension_check_layout = self.extension_check_button_layout()
        bottom_layout.addLayout(extension_check_layout)
        bottom_layout.addStretch()

        self.main_layout.addLayout(bottom_layout)

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

        layout.addWidget(button)

        return layout

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

    def extension_check_button_layout(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 0, 0, 0) 
        layout.setAlignment(Qt.AlignLeft)

        button = QPushButton()
        button.setObjectName("extension_check")
        button.setToolTip("확장자 검사")
        button.setSizePolicy(self.size_policy)
        button.setIcon(QIcon(image_base_path("extension_check.png")))
        button.setFixedSize(30, 30)

        layout.addWidget(button)
        
        return layout
