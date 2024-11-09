import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QApplication, QMessageBox
from PyQt5.QtGui import QFont
from .password_manager import PasswordManager

class SecureFolderManager:
    def __init__(self):
        # 보안 폴더 경로를 고정된 경로로 설정
        self.secure_folder_path = os.path.join(os.path.expanduser("~"), "SecureFolder")
        self.authenticated = False  # 인증 여부를 저장하는 변수
        self.pwd_mgr = PasswordManager()

        # 보안 폴더가 없으면 생성
        if not os.path.exists(self.secure_folder_path):
            os.makedirs(self.secure_folder_path)

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
    