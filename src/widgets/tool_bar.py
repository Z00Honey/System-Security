from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSizePolicy, QMenu,
    QAction, QMessageBox, QProgressDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path
from utils.analysis import analyze_file
from utils.virus_scan import VirusScanThread
from dotenv import load_dotenv
import os


class ToolBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # Load environment variables from .env file
        load_dotenv()

        self.setObjectName("tool_bar")
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.create_toolbar_buttons()
        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("tool_bar.css"))

        self.setFixedHeight(40)  # 툴바 높이 설정
        self.setFixedWidth(1000)  # 툴바 너비 설정 (예시, 필요에 따라 조정)

    def create_toolbar_buttons(self):
        button_info = [
            {"name": "new_folder", "icon": "new_folder.png"},
            {"name": "cut", "icon": "cut.png"},
            {"name": "copy", "icon": "copy.png"},
            {"name": "paste", "icon": "paste.png"},
            {"name": "rename", "icon": "rename.png"},
            #{"name": "share", "icon": "share.png"},
            {"name": "delete", "icon": "delete.png"},
            {"name": "shield", "icon": "shield.png", "menu": True},
            #{"name": "lock", "icon": "lock.png"},
            #{"name": "memo", "icon": "memo.png"},
            #{"name": "view_more", "icon": "view_more.png"},
        ]

        for info in button_info:
            button = QPushButton()
            button.setIcon(QIcon(image_base_path(info["icon"])))
            if info["name"] == "memo":
                button.setIconSize(QSize(36, 36))
            elif info["name"] == "shield":
                button.setIconSize(QSize(32, 32))
            else:
                button.setIconSize(QSize(28, 28))
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            self.layout.addWidget(button)

            if info["name"] in ["copy", "paste", "cut"]:
                event = getattr(self, f'file_{info["name"]}')
                button.clicked.connect(event)

            if info.get("menu") and info["name"] == "shield":
                menu = QMenu(button)

                extension_action = QAction("확장자 검사", menu)
                virus_action = QAction("바이러스 검사", menu)

                extension_action.triggered.connect(self.run_extension_check)
                virus_action.triggered.connect(self.run_virus_check)

                menu.addAction(extension_action)
                menu.addAction(virus_action)

                button.setMenu(menu)

            self.layout.addWidget(button)

    def file_copy(self):
        self.parent.file_event('copy')

    def file_cut(self):
        self.parent.file_event('cut')

    def file_paste(self):
        self.parent.file_event('paste')

    def file_delete(self):
        self.parent.file_event('delete')

    def run_extension_check(self):
        # MainWindow 인스턴스 찾기
        main_window = self.window()

        # 현재 선택된 파일 가져오기
        current_index = main_window.file_explorer_bar.file_area.file_list.tree_view.currentIndex()
        if not current_index.isValid():
            # QMessageBox 생성
            message_box = QMessageBox(self)
            message_box.setWindowTitle("경고")
            message_box.setText("파일을 선택해주세요.")
            message_box.setIcon(QMessageBox.Warning)
            message_box.setStandardButtons(QMessageBox.Ok)

            # "OK" 버튼 텍스트를 "확인"으로 변경
            message_box.button(QMessageBox.Ok).setText("확인")

            # 메시지박스 실행
            message_box.exec_()
            return

        file_path = main_window.file_explorer_bar.file_area.file_list.model.filePath(current_index)
        
        if main_window.file_explorer_bar.file_area.file_list.model.isDir(current_index):
            # QMessageBox 생성
            message_box = QMessageBox(self)
            message_box.setWindowTitle("경고")
            message_box.setText("파일만 검사할 수 있습니다.")
            message_box.setIcon(QMessageBox.Warning)
            message_box.setStandardButtons(QMessageBox.Ok)

            # "OK" 버튼 텍스트를 "확인"으로 변경
            message_box.button(QMessageBox.Ok).setText("확인")

            # 메시지박스 실행
            message_box.exec_()
            return


        # QMessageBox 객체 생성
        message_box = QMessageBox(self)
        message_box.setWindowTitle("확장자 검사")
        message_box.setText(f"선택한 파일에 대한 포맷 및 확장자 불일치 검사를 진행하시겠습니까?")
         # 아이콘 설정
        custom_icon_path = image_base_path("shield.png")  # src/assets/images/shield.png를 기준으로 동작
        message_box.setIconPixmap(QPixmap(custom_icon_path))  # 커스텀 아이콘 설정


        # 표준 버튼 추가
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # 버튼 텍스트 변경
        message_box.button(QMessageBox.Yes).setText("예")
        message_box.button(QMessageBox.No).setText("아니요")

        # 메시지박스 실행
        reply = message_box.exec_()
    
        if reply == QMessageBox.Yes:
    
            # 파일 분석 실행
            result = analyze_file(file_path)

            # 검사 완료 후 결과 메시지 박스
            result_message = QMessageBox(self)
            result_message.setWindowTitle("확장자 검사 결과")
            result_message.setText(result)
            result_message.setIcon(QMessageBox.Information)
            result_message.setStandardButtons(QMessageBox.Ok)

            # "확인" 버튼 텍스트 변경
            result_message.button(QMessageBox.Ok).setText("확인")
            result_message.exec_()

    def run_virus_check(self):
        main_window = self.window()
        current_index = main_window.file_explorer_bar.file_area.file_list.tree_view.currentIndex()
        
        if not current_index.isValid():
            QMessageBox.warning(self, "경고", "파일이나 폴더를 선택해주세요.")
            return

        path = main_window.file_explorer_bar.file_area.file_list.model.filePath(current_index)
        
        # 선택한 경로가 폴더인지 확인
        if main_window.file_explorer_bar.file_area.file_list.model.isDir(current_index):
            
        # 폴더 내부 파일 확인
            folder_content = os.listdir(path)
            files_only = [f for f in folder_content if os.path.isfile(os.path.join(path, f))]

            if not files_only:
                # QMessageBox 생성
                message_box = QMessageBox(self)
                message_box.setWindowTitle("정보")
                message_box.setText("선택한 폴더에 파일이 없습니다.")
                message_box.setIcon(QMessageBox.Information)
                message_box.setStandardButtons(QMessageBox.Ok)

                # "확인" 버튼 텍스트 변경
                message_box.button(QMessageBox.Ok).setText("확인")

                # 메시지박스 실행
                message_box.exec_()
                return
            
        # QMessageBox 객체 생성
        message_box = QMessageBox(self)
        message_box.setWindowTitle("바이러스토탈을 이용한 평판 검사")
        message_box.setText("선택한 파일/폴더에 대한 바이러스토탈 평판 검사를 진행하시겠습니까?")
         # 아이콘 설정
        custom_icon_path = image_base_path("shield.png")  # src/assets/images/shield.png를 기준으로 동작
        message_box.setIconPixmap(QPixmap(custom_icon_path))  # 커스텀 아이콘 설정

        # 표준 버튼 추가
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # 버튼 텍스트 변경
        message_box.button(QMessageBox.Yes).setText("예")
        message_box.button(QMessageBox.No).setText("아니요")

        # 메시지박스 실행
        reply = message_box.exec_()

        if reply == QMessageBox.Yes:
            self.progress_dialog = QProgressDialog("검사 중...", "취소", 0, 100, self)
            self.progress_dialog.setWindowTitle("바이러스토탈을 이용한 평판 검사")
            self.progress_dialog.setWindowModality(True)
            
            self.scan_thread = VirusScanThread(path)
            self.scan_thread.finished.connect(self.on_scan_finished)
            self.scan_thread.error.connect(self.on_scan_error)
            self.scan_thread.progress.connect(self.update_progress)
            
            self.progress_dialog.canceled.connect(self.scan_thread.terminate)
            self.scan_thread.start()
            self.progress_dialog.show()

    def update_progress(self, current, total):
        if self.progress_dialog:
            progress = int((current / total) * 100)
            self.progress_dialog.setValue(progress)
            self.progress_dialog.setLabelText(f"검사 중... ({current}/{total})")

    def on_scan_finished(self, result):
        self.progress_dialog.close()

        # QMessageBox 객체 생성
        message_box = QMessageBox(self)
        message_box.setWindowTitle("검사 완료")
        message_box.setText(result)
        message_box.setIcon(QMessageBox.Information)
        message_box.setStandardButtons(QMessageBox.Ok)

        # "OK" 버튼 텍스트 변경
        message_box.button(QMessageBox.Ok).setText("확인")

        # 메시지박스 실행
        message_box.exec_()

    def on_scan_error(self, error_message):
        self.progress_dialog.close()

        # QMessageBox 생성
        message_box = QMessageBox(self)
        message_box.setWindowTitle("오류")
        message_box.setText(f"검사 중 오류가 발생했습니다:\n{error_message}")
        message_box.setIcon(QMessageBox.Critical)
        message_box.setStandardButtons(QMessageBox.Ok)

        # "OK" 버튼 텍스트를 "확인"으로 변경
        message_box.button(QMessageBox.Ok).setText("확인")

        # 메시지박스 실행
        message_box.exec_()
