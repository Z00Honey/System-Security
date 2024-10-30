from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation
from PyQt5.QtGui import QMouseEvent
import sys

class DraggableTab(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFixedSize(150, 50)
        self.label = QLabel(title, self)
        self.label.setAlignment(Qt.AlignCenter)

class WidgetNewTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setContentsMargins(0, 0, 0, 0)
        
        # 드래그 관련 상태
        self.dragging_tab = None
        self.original_pos = QPoint()
        self.offset = QPoint()
        self.tabs = []

    def add_tab_widget(self, title):
        tab = DraggableTab(title)
        self.tabs.append(tab)
        self.layout.addWidget(tab)

    def mousePressEvent(self, event: QMouseEvent):
        widget = self.childAt(event.pos())
        if isinstance(widget, DraggableTab):
            self.dragging_tab = widget
            self.original_pos = widget.pos()
            self.offset = event.pos() - self.original_pos
            widget.raise_()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging_tab:
            new_pos = event.pos() - self.offset
            self.dragging_tab.move(new_pos)

            # 위치 교환 처리
            for tab in self.tabs:
                if tab != self.dragging_tab and tab.geometry().contains(event.pos()):
                    self.swap_tabs(self.dragging_tab, tab)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.dragging_tab:
            # 드래그 종료 후 원래 위치로 애니메이션
            anim = QPropertyAnimation(self.dragging_tab, b"pos")
            anim.setEndValue(self.original_pos)
            anim.setDuration(200)
            anim.start()

            self.dragging_tab = None

    def swap_tabs(self, tab1, tab2):
        # 두 탭의 위치를 애니메이션과 함께 교환
        index1 = self.layout.indexOf(tab1)
        index2 = self.layout.indexOf(tab2)

        if index1 != -1 and index2 != -1:
            self.layout.removeWidget(tab1)
            self.layout.removeWidget(tab2)
            
            # 위치 교환 후 애니메이션
            self.layout.insertWidget(index1, tab2)
            self.layout.insertWidget(index2, tab1)

            anim1 = QPropertyAnimation(tab1, b"pos")
            anim1.setEndValue(tab2.pos())
            anim1.setDuration(200)
            anim1.start()

            anim2 = QPropertyAnimation(tab2, b"pos")
            anim2.setEndValue(tab1.pos())
            anim2.setDuration(200)
            anim2.start()

# 테스트 실행 코드
app = QApplication(sys.argv)
window = WidgetNewTab()
for i in range(5):
    window.add_tab_widget(f"Tab {i+1}")
window.show()
sys.exit(app.exec_())
