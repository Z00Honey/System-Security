from ctypes.wintypes import POINT
import ctypes

import win32con
import win32gui

from PyQt5.QtCore import QByteArray, QPoint, Qt, QEvent
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication
from PyQt5.QtGui import QMouseEvent

from utils.native.util import isMaximized, isFullScreen
from utils.native.c_structure import LPNCCALCSIZE_PARAMS

from widgets.titlebar.title_bar import MaximizeButtonState
from widgets.titlebar.tabs import TabWidgetState

def _nativeEvent(widget: QWidget, event_type: QByteArray, message: int):
    msg = ctypes.wintypes.MSG.from_address(message.__int__())

    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    r = widget.devicePixelRatioF()
    x = pt.x / r - widget.x()
    y = pt.y / r - widget.y()

    user32 = ctypes.windll.user32
    dpi = user32.GetDpiForWindow(msg.hWnd)
    borderWidth = user32.GetSystemMetricsForDpi(win32con.SM_CXSIZEFRAME, dpi) + user32.GetSystemMetricsForDpi(92, dpi)
    borderHeight = user32.GetSystemMetricsForDpi(win32con.SM_CYSIZEFRAME, dpi) + user32.GetSystemMetricsForDpi(92, dpi)

    if msg.message == win32con.WM_NCHITTEST:
        if widget.isResizable() and not isMaximized(msg.hWnd):
            w, h = widget.width(), widget.height()
            lx = x < borderWidth
            rx = x > w - borderWidth
            ty = y < borderHeight
            by = y > h - borderHeight

            if lx and ty:
                return True, win32con.HTTOPLEFT
            if rx and by:
                return True, win32con.HTBOTTOMRIGHT
            if rx and ty:
                return True, win32con.HTTOPRIGHT
            if lx and by:
                return True, win32con.HTBOTTOMLEFT
            if ty:
                return True, win32con.HTTOP
            if by:
                return True, win32con.HTBOTTOM
            if lx:
                return True, win32con.HTLEFT
            if rx:
                return True, win32con.HTRIGHT

        if widget.childAt(QPoint(x, y)) is widget.title_bar.MAXIMIZE_BUTTON:
            widget.title_bar.MAXIMIZE_BUTTON.setState(MaximizeButtonState.HOVER)
            return True, win32con.HTMAXBUTTON
        
        if (point := widget.childAt(QPoint(x,y))) in widget.title_bar.newtab_widget.tabs:

            tabs = widget.title_bar.newtab_widget.tabs

            for tab in tabs:
                if point is tab:
                    print("TabWidgetState.HOVER")
                    widget.title_bar.newtab_widget.setState(TabWidgetState.HOVER, tab)
                else:
                    widget.title_bar.newtab_widget.setState(TabWidgetState.NORMAL, tab)
        
        for tab in widget.title_bar.newtab_widget.tabs:
            if widget.childAt(QPoint(x,y)) is tab.findChild(QPushButton):
                widget.title_bar.newtab_widget.setState(TabWidgetState.HOVER, tab)
            
        if widget.childAt(x, y) not in widget.title_bar.findChildren(QPushButton):
            if borderHeight < y < widget.title_bar.height():
                return True, win32con.HTCAPTION

    elif msg.message in [0x2A2, win32con.WM_MOUSELEAVE]:
        widget.title_bar.MAXIMIZE_BUTTON.setState(MaximizeButtonState.NORMAL)
        # if not ((point := widget.childAt(QPoint(x,y))) in widget.title_bar.newtab_widget.tabs):
        #     for tab in widget.title_bar.newtab_widget.tabs:
        #         if not widget.childAt(QPoint(x,y)) is tab.findChild(QPushButton):
        #             if point is tab:
        #                 widget.title_bar.newtab_widget.setState(TabWidgetState.NORMAL, None)
        widget.title_bar.newtab_widget.setState(TabWidgetState.NORMAL, None)
        # Tlqkf
                

    elif msg.message == win32con.WM_MOVE:
        win32gui.SetWindowPos(msg.hWnd, None, 0, 0, 0, 0, win32con.SWP_NOMOVE |
                              win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)

    elif msg.message in [win32con.WM_NCLBUTTONDOWN, win32con.WM_NCLBUTTONDBLCLK]:
        if widget.childAt(QPoint(x, y)) is widget.title_bar.MAXIMIZE_BUTTON:
            QApplication.sendEvent(widget.title_bar.MAXIMIZE_BUTTON, QMouseEvent(
                QEvent.MouseButtonPress, QPoint(), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier))
            return True, 0
    elif msg.message in [win32con.WM_NCLBUTTONUP, win32con.WM_NCRBUTTONUP]:
        if widget.childAt(QPoint(x, y)) is widget.title_bar.MAXIMIZE_BUTTON:
            QApplication.sendEvent(widget.title_bar.MAXIMIZE_BUTTON, QMouseEvent(
                QEvent.MouseButtonRelease, QPoint(), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier))

    elif msg.message == win32con.WM_NCCALCSIZE:
        rect = ctypes.cast(msg.lParam, LPNCCALCSIZE_PARAMS).contents.rgrc[0]

        isMax = isMaximized(msg.hWnd)
        isFull = isFullScreen(msg.hWnd)

        if isMax and not isFull:
            rect.top += borderHeight
            rect.left += borderWidth
            rect.right -= borderWidth
            rect.bottom -= borderHeight

        result = 0 if not msg.wParam else win32con.WVR_REDRAW
        return True, win32con.WVR_REDRAW

    return False, 0
