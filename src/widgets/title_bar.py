from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QSizePolicy, QSpacerItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPalette, QColor

from enum import IntEnum, auto, Enum

from utils.load import load_stylesheet, image_base_path

class MaximizeButtonState(IntEnum):
    HOVER = auto()
    NORMAL = auto()

class MaximizeButtonIcon(str, Enum):
    RESTORE = "restore"
    MAXIMIZE = "maximize"

class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.background_color = "#d9f3ff"

        self.setFixedHeight(50)

        self.title_bar()
        self.window_controls()
        
    def title_bar(self):
        palette = self.palette()
        palette.setColor(
            QPalette.Background, 
            QColor(self.background_color)
        )
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def window_controls(self):

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

            button = getattr(self, name)

            button.setIcon(QIcon(image_base_path(filename)))

            size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed) # Set PyQt5 CSS Access Policy 
            button.setSizePolicy(size_policy)
            button.setObjectName(name)

            controls_layout.addWidget(button)

        self.MINIZE_BUTTON.clicked.connect(self.parent.showMinimized)
        self.MAXIMIZE_BUTTON.clicked.connect(self.maximize_button_event)
        self.CLOSE_BUTTON.clicked.connect(self.parent.close)

        main_layout = QVBoxLayout()
        main_layout.addLayout(controls_layout)
        main_layout.addStretch()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        self.setStyleSheet(load_stylesheet("title_bar.css"))

    def maximize_button_event(self):
        status = self.parent.isMaximized()

        if status:
            self.parent.showNormal()
            self.set_maximize_button_icon(MaximizeButtonIcon.MAXIMIZE)
        else:
            self.parent.showMaximized()
            self.set_maximize_button_icon(MaximizeButtonIcon.RESTORE)

    def set_maximize_button_icon(self, status):
        if status == MaximizeButtonIcon.MAXIMIZE:
            self.MAXIMIZE_BUTTON.setIcon(
                QIcon( image_base_path(self.CONTROLS_ICONS['MAXIMIZE_BUTTON']) )
            )
        elif status == MaximizeButtonIcon.RESTORE:
            self.MAXIMIZE_BUTTON.setIcon(
                QIcon( image_base_path(self.CONTROLS_ICONS['NORMAL_BUTTON']) )
            )

    def minimze_button_event(self):
        self.parent.showMinimized()