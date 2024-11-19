import os
import subprocess
import shutil
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QApplication, QMessageBox
from PyQt5.QtGui import QFont
from .password_manager import PasswordManager  # 기존 import 유지
from .ProcessAES import AESManager
from .Mapping import MappingManager

class SecureFolderManager:
    def __init__(self):
        # 보안 폴더 경로 설정
        self.folder_name = "SystemUtilities"  # 폴더 이름 복원
        self.secure_folder_path = os.path.join(
            os.path.expanduser("~"),
            "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", self.folder_name
        )
        self.authenticated = False  # 인증 여부를 저장하는 변수
        self.pwd_mgr = PasswordManager()  # PasswordManager 인스턴스 생성
        self.AES_mgr = AESManager()
        self.mapping_mgr = MappingManager()

        # 보안 폴더가 없으면 생성
        if not os.path.exists(self.secure_folder_path):
            os.makedirs(self.secure_folder_path)  # 보안 폴더 생성
            self._hide_folder(self.secure_folder_path)  # 폴더 숨김 처리
            

    def _hide_folder(self, folder_path):
        # 폴더 숨김 처리
        if os.name == 'nt':  # Windows 환경에서만 작동
            try:
                subprocess.run(['attrib', '+h', folder_path], check=True)
                print(f"Folder '{folder_path}' is now hidden.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to hide folder: {e}")
    
    #################################################인증↓↓↓↓
    def authenticate(self):
        if not self.pwd_mgr.setup:
            self.pwd_mgr.set_initial_password()
            return

        dialog = QDialog()
        dialog.setWindowTitle("보안폴더접근")
        dialog.setFixedSize(400, 200)
        
        layout = QVBoxLayout()

        # 비밀번호 입력 레이블 및 입력 필드
        label = QLabel("비밀번호 입력:")
        label_font = QFont("Arial", 12)
        label.setFont(label_font)
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setFont(QFont("Arial", 12))
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        temp_auth_button = QPushButton("임시인증 하기")
        temp_auth_button.setFont(QFont("Arial", 10))
        temp_auth_button.clicked.connect(lambda: self.temp_auth(dialog))
        cancel_button = QPushButton("취소")
        cancel_button.setFont(QFont("Arial", 10))
        confirm_button = QPushButton("확인")
        confirm_button.setFont(QFont("Arial", 10))
        confirm_button.setDefault(True)  # "확인" 버튼을 기본으로 설정
        
        # 버튼 클릭 이벤트 연결
        cancel_button.clicked.connect(dialog.reject)
        confirm_button.clicked.connect(lambda: self.verify_password(password_input.text(), dialog))
        
        button_layout.addWidget(temp_auth_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(confirm_button)
        
        # 레이아웃 설정
        layout.addWidget(label)
        layout.addWidget(password_input)
        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            self.authenticated = True
            return True
        return False

    def verify_password(self, password, dialog):
        if self.pwd_mgr.authenticate_user(password):
            dialog.accept()
        else:
            QMessageBox.warning(dialog, "인증 실패", "비밀번호가 일치하지 않습니다.")


    def temp_auth(self, dialog):
        # 이메일 인증 코드 전송
        self.pwd_mgr.send_verification_code()
        verification_dialog = QDialog()
        verification_dialog.setWindowTitle("인증 코드 확인")
        verification_dialog.setFixedSize(400, 150)
        
        layout = QVBoxLayout()

        # 인증 코드 입력 필드
        label = QLabel("인증 코드를 입력하세요:")
        label_font = QFont("Arial", 12)
        label.setFont(label_font)
        verification_code_input = QLineEdit()
        verification_code_input.setFont(QFont("Arial", 12))
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        confirm_button = QPushButton("확인")
        confirm_button.setFont(QFont("Arial", 10))
        cancel_button = QPushButton("취소")
        cancel_button.setFont(QFont("Arial", 10))
        
        # 버튼 클릭 이벤트 연결
        cancel_button.clicked.connect(verification_dialog.reject)
        confirm_button.clicked.connect(lambda: self.verify_code(verification_code_input.text(), verification_dialog))
        
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)
        
        # 레이아웃 설정
        layout.addWidget(label)
        layout.addWidget(verification_code_input)
        layout.addLayout(button_layout)
        verification_dialog.setLayout(layout)

        if verification_dialog.exec_() == QDialog.Accepted:
            self.authenticated = True
            dialog.accept()
        
            

    def verify_code(self, code, dialog):
        if code == self.pwd_mgr.correct_verification_code:
            dialog.accept()
        else:
            QMessageBox.warning(dialog, "인증 실패", "인증 코드가 일치하지 않습니다.")
    #################################################인증↑↑↑↑
    
    def lock(self, path):
        # 파일 또는 폴더를 보안 폴더로 이동하고 암호화
        if self.AES_mgr.pm.AESkey is None:
            QMessageBox.warning(None, "경고", "AES 키가 설정되지 않았습니다.")
            return

        if not os.path.exists(path):
            QMessageBox.warning(None, "경고", "경로가 존재하지 않습니다.")
            return

        try:
            if os.path.isdir(path):  # 폴더 처리
                folder_name = os.path.basename(path)
                secure_folder = os.path.join(self.secure_folder_path, folder_name)

                # 폴더 자체 이동
                shutil.move(path, secure_folder)

                # 폴더 및 파일 메타데이터 기록
                for root, _, files in os.walk(secure_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        original_path = os.path.join(path, os.path.relpath(file_path, secure_folder))
                        self._lock_file(file_path, original_path)

                QMessageBox.information(None, "성공", f"해당 파일/폴더를 잠금합니다.")

            else:  # 단일 파일 처리
                # 단일 파일 이동
                filename = os.path.basename(path)
                secure_path = os.path.join(self.secure_folder_path, filename)
                os.makedirs(os.path.dirname(secure_path), exist_ok=True)
                shutil.move(path, secure_path)

                # 메타데이터 기록 및 암호화
                self._lock_file(secure_path, path)

        except Exception as e:
            QMessageBox.critical(None, "오류", f"파일 암호화 또는 이동 중 오류 발생: {e}")

    def _lock_file(self, file_path, original_path):
        # 단일 파일을 보안 폴더로 이동하고 암호화
        file_id = self.mapping_mgr.generate_id(original_path)  # 고유 ID 생성
        self.mapping_mgr.mapping[file_id] = {"original_path": original_path}
        self.mapping_mgr.save_mapping()

        # 암호화 수행
        self.AES_mgr.encrypt(file_path)

    def unlock(self, path):
        # 보안 폴더 내의 파일 또는 폴더를 원래 위치로 복원하고 복호화
        if not os.path.exists(path):
            QMessageBox.warning(None, "경고", "경로가 존재하지 않습니다.")
            return

        try:
            if os.path.isdir(path):  # 폴더 처리
                for root, _, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        self._unlock_file(file_path)

                # 보안 폴더 내 폴더 삭제
                shutil.rmtree(path)

            else:  # 단일 파일 처리
                self._unlock_file(path)

            QMessageBox.information(None, "성공", f"해당 파일/폴더를 해제합니다")
        except Exception as e:
            QMessageBox.critical(None, "오류", f"파일 복호화 또는 이동 중 오류 발생: {e}")

    def _unlock_file(self, file_path):
        # 단일 파일을 원래 위치로 복원하고 복호화
        filename = os.path.basename(file_path)
        file_id = self.mapping_mgr.get_file_id(filename)

        if file_id is None:
            QMessageBox.warning(None, "경고", "해당 파일의 원래 경로를 찾을 수 없습니다.")
            return

        original_path = self.mapping_mgr.get_original_path(file_id)  # 원래 경로 검색
        if original_path is None:
            QMessageBox.warning(None, "경고", "원래 경로를 찾을 수 없습니다.")
            return

        # 폴더 경로가 없으면 재생성
        original_folder = os.path.dirname(original_path)
        if not os.path.exists(original_folder):
            os.makedirs(original_folder)

        # 파일 이동 및 복호화
        shutil.move(file_path, original_path)
        self.AES_mgr.decrypt(original_path)  # 복호화 수행

        # 매핑 정보 삭제
        self.mapping_mgr.delete_mapping(file_id)
        self.mapping_mgr.save_mapping()

      
