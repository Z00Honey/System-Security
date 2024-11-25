from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSizePolicy, QMenu,
    QAction, QMessageBox, QProgressDialog
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path
from ctypes import cdll, c_char_p, create_string_buffer, c_bool, c_size_t
from dotenv import load_dotenv
import os


class ToolBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
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
            {"name": "share", "icon": "share.png"},
            {"name": "delete", "icon": "delete.png"},
            {"name": "shield", "icon": "shield.png", "menu": True},
            {"name": "lock", "icon": "lock.png"},
            {"name": "memo", "icon": "memo.png"},
            {"name": "view_more", "icon": "view_more.png"},
        ]

        for info in button_info:
            button = QPushButton()
            button.setIcon(QIcon(image_base_path(info["icon"])))
            button.setIconSize(QSize(32, 32))
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            
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

    def run_extension_check(self):
        # MainWindow 인스턴스 찾기
        main_window = self.window()
        
        # 현재 선택된 파일 가져오기
        current_index = main_window.file_list.currentIndex()
        if not current_index.isValid():
            QMessageBox.warning(self, "경고", "파일을 선택해주세요.")
            return

        file_path = main_window.file_list.model.filePath(current_index)
        if main_window.file_list.model.isDir(current_index):
            QMessageBox.warning(self, "경고", "파일만 검사할 수 있습니다.")
            return
            
        # 확인 메시지 표시
        reply = QMessageBox.question(
            self, 
            '확장자 검사', 
            f'선택한 파일을 검사하시겠습니까?\n\n파일: {file_path}',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 파일 분석 실행
            result = analyze_file(file_path)
            QMessageBox.information(self, "분석 결과", result)

    def run_virus_check(self):
        # MainWindow 인스턴스 찾기
        main_window = self.window()
        
        # 현재 선택된 파일 또는 폴더 가져오기
        current_index = main_window.file_list.currentIndex()
        if not current_index.isValid():
            QMessageBox.warning(self, "경고", "파일이나 폴더를 선택해주세요.")
            return

        path = main_window.file_list.model.filePath(current_index)

        # 확인 메시지 표시
        reply = QMessageBox.question(
            self, 
            "바이러스토탈을 이용한 평판 검사", 
            "선택한 파일/폴더에 대한 바이러스토탈 평판 검사를 진행하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if os.path.isdir(path):
                self.perform_folder_scan(path)
            else:
                self.perform_file_scan(path)

    def perform_file_scan(self, file_path):
        """단일 파일 검사"""
        # DLL 로드
        dll_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'build', 'vrsapi1.dll')
        vrs_dll = cdll.LoadLibrary(dll_path)

        scan_file = vrs_dll.scan_file_virustotal
        scan_file.argtypes = [c_char_p, c_char_p, c_size_t]
        scan_file.restype = c_bool

        result_buffer = create_string_buffer(4096)
        file_path_bytes = file_path.encode('utf-8')

        # 바이러스 검사 수행
        success = scan_file(file_path_bytes, result_buffer, 4096)

        # 검사 결과 처리
        if success:
            result = result_buffer.value.decode('utf-8')
            QMessageBox.information(self, "바이러스 검사 결과", result)
        else:
            error_msg = result_buffer.value.decode('utf-8', errors='replace')
            QMessageBox.warning(self, "검사 실패", f"바이러스 검사 중 오류가 발생했습니다.\n{error_msg}")

    def perform_folder_scan(self, folder_path):
        """폴더 내 모든 파일을 검사한 결과를 한 번에 출력"""
        results = []
        all_files = [
            os.path.join(root, file)
            for root, _, files in os.walk(folder_path) for file in files
        ]

        # 진행 바 생성
        progress_dialog = QProgressDialog("검사 중...", "취소", 0, len(all_files), self)
        progress_dialog.setWindowTitle("바이러스토탈을 이용한 평판 검사")
        progress_dialog.setWindowModality(True)
        progress_dialog.setValue(0)

        for i, file_path in enumerate(all_files, 1):
            if progress_dialog.wasCanceled():
                QMessageBox.warning(self, "경고", "검사가 취소되었습니다.")
                return  # 검사 중단

            # 파일 검사 수행
            result = self.perform_file_scan_result(file_path)
            results.append(result)
            progress_dialog.setValue(i)
            progress_dialog.setLabelText(f"검사 중... ({i}/{len(all_files)})")

        progress_dialog.close()

        # 검사 완료 메시지
        QMessageBox.information(
            self,
            "바이러스토탈을 이용한 평판 검사",
            "검사가 완료되었습니다.\n악성 파일이 있는 경우 조치를 취하세요."
        )

        # 결과 출력
        QMessageBox.information(self, "폴더 검사 결과", "\n\n".join(results))

    def perform_file_scan_result(self, file_path):
        """파일 검사 결과 반환"""
        dll_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'build', 'vrsapi1.dll')
        vrs_dll = cdll.LoadLibrary(dll_path)

        scan_file = vrs_dll.scan_file_virustotal
        scan_file.argtypes = [c_char_p, c_char_p, c_size_t]
        scan_file.restype = c_bool

        result_buffer = create_string_buffer(4096)
        file_path_bytes = file_path.encode('utf-8')

        success = scan_file(file_path_bytes, result_buffer, 4096)

        if success:
            return result_buffer.value.decode('utf-8')
        else:
            return f"파일: {file_path}\n오류 발생"
