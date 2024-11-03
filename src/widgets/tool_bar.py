from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy
from utils.load import load_stylesheet

class ToolBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0) 
        self.setLayout(self.layout)
        
        self.create_buttons()

    #test version
    def create_buttons(self):
        button_names = ['New', 'Open', 'Save', 'Delete', 'Copy', 'Paste']
        
        for name in button_names:
            button = QPushButton(name)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred) 
            self.layout.addWidget(button)  

        self.setLayout(self.layout)
