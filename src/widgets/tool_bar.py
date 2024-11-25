from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path
from ctypes import cdll, c_char_p, create_string_buffer, c_bool, c_size_t
from utils.analysis import analyze_file
from dotenv import load_dotenv
import os
import json


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
        reply = QMessageBox.question(self, 
                                   '확장자 검사', 
                                   f'선택한 파일을 검사하시겠습니까?\n\n파일: {file_path}',
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 파일 분석 실행
            result = analyze_file(file_path)
            QMessageBox.information(self, "분석 결과", result)

    def run_virus_check(self):
        # MainWindow 인스턴스 찾기
        main_window = self.window()
        
        # 현재 선택된 항목 가져오기
        current_index = main_window.file_list.currentIndex()
        if not current_index.isValid():
            QMessageBox.warning(self, "경고", "파일 또는 폴더를 선택해주세요.")
            return

        selected_path = main_window.file_list.model.filePath(current_index)

        if main_window.file_list.model.isDir(current_index):
            self.perform_folder_scan(selected_path)
        else:
            self.perform_file_scan(selected_path)

    def perform_file_scan(self, file_path):
        """파일 검사 결과를 바로 출력"""
        result = self.perform_virus_scan(file_path)
        QMessageBox.information(self, "바이러스 검사 결과", result)

    def perform_folder_scan(self, folder_path):
        """폴더 내 모든 파일을 검사한 결과를 한 번에 출력"""
        results = []
        for root, _, files in os.walk(folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                result = self.perform_virus_scan(file_path)
                results.append(result)

        # 모든 검사 결과를 모아서 표시
        QMessageBox.information(self, "폴더 검사 결과", "\n\n".join(results))

    def perform_virus_scan(self, file_path):
        """파일 경로를 받아 바이러스 검사를 수행"""
        file_name = os.path.basename(file_path)

        try:
            dll_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'build', 'vrsapi1.dll')
            print("DLL Path:", dll_path)  # DLL 경로 출력
            vrs_dll = cdll.LoadLibrary(dll_path)

            scan_file = vrs_dll.scan_file_virustotal
            scan_file.argtypes = [c_char_p, c_char_p, c_size_t]
            scan_file.restype = c_bool

            result_buffer = create_string_buffer(65536)
            file_path_bytes = file_path.encode('utf-8')

            success = scan_file(file_path_bytes, result_buffer, 65536)

            if success:
                try:
                    result = result_buffer.value.decode('utf-8')
                    json_data = json.loads(result)
                    return self.parse_scan_result(json_data, file_name)
                except (UnicodeDecodeError, json.JSONDecodeError) as e:
                    raw_data = result_buffer.raw
                    print("[DEBUG] Raw Data:", raw_data)  # 원본 데이터 출력
                    return f"파일: {file_name}\n결과 처리 중 오류 발생: {str(e)}"
            else:
                try:
                    error_msg = result_buffer.value.decode('utf-8')
                except UnicodeDecodeError:
                    error_msg = result_buffer.value.decode('latin1', errors='replace')
                return f"파일: {file_name}\n검사 실패: {error_msg}"
        except Exception as e:
            return f"파일: {file_name}\nDLL 오류: {str(e)}"

    def parse_scan_result(self, json_data, file_name):
        """결과 JSON에서 탐지된 엔진과 검사 상태만 출력"""
        try:
            attributes = json_data.get("data", {}).get("attributes", {})
            stats = attributes.get("last_analysis_stats", {})

            total_engines = sum(stats.values())
            detected = stats.get("malicious", 0)
            
            detection_summary = f"{detected}/{total_engines}"
            result_status = "위험 없음" if detected == 0 else "위험 있음"

            return f"이름: {file_name}\n탐지된 엔진: {detection_summary}\n검사 상태: {result_status}"
        except KeyError as e:
            return f"결과 처리 중 오류 발생: {str(e)}"
