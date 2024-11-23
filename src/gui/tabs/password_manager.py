from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton,
    QProgressDialog, QMessageBox, QApplication,
    QCheckBox, QDialogButtonBox)
from PyQt5.QtCore import Qt, QTimer
import re
import sys
import smtplib
import random
from email.mime.text import MIMEText
import ctypes
from ctypes import c_char_p, POINTER, c_ubyte, c_int
import os
import json
import stat
from .Thread import TaskRunner


class PasswordManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
    def __init__(self):
        self.setup = False
        self.password_hash = None
        self.salt = None
        self.email = None
        self.AESkey = None
        self.correct_verification_code = None
        self.timer = None
        self.remaining_time = 0
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        self.secure_folder_path = os.path.join(
            os.path.expanduser("~"),
            "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "SystemUtilities"
        )

        #################################################DLL설정↓↓↓↓
        # DLL 로드 및 해시 함수 정의 (세 개의 인자 받도록 수정)
        current_directory = os.path.dirname(__file__)
        dll_path = os.path.join(current_directory, 'hashing.dll')
        self.hasher = ctypes.CDLL(dll_path)
        
        dll_path1 = os.path.join(current_directory, 'salthide.dll')
        self.salthide = ctypes.CDLL(dll_path1)

        self.hasher.hash_password.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_ubyte)]
        self.hasher.hash_password.restype = None

        self.salthide.encrypt_message.argtypes = [c_char_p, POINTER(c_ubyte)]
        self.salthide.encrypt_message.restype = c_int

        self.salthide.decrypt_message.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_int]
        self.salthide.decrypt_message.restype = c_int

        self.load_config()
        self.load_key()
    #################################################dll설정↑↑↑↑

    #################################################초기설정↓↓↓↓
    def set_initial_password(self, parent=None):
        # 비밀번호 초기 설정 창
        dialog = QDialog(parent)
        dialog.setWindowTitle("보안폴더 시작하기")
        dialog.setFixedSize(400, 500)  # 다이얼로그 크기 조금 확대

        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)  # 요소 간 간격 줄이기

        welcome_label = QLabel("안녕하세요!\n보안 폴더에 오신 것을 환영합니다!\n처음 사용을 위한 간단한 설정을 진행해 주세요.")
        welcome_label.setStyleSheet("font-size: 12pt; font-family: Arial;")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setWordWrap(True)  # 텍스트가 잘리지 않도록 자동 줄 바꿈 활성화
        welcome_label.setFixedHeight(100)  # 레이블 높이 조정
        main_layout.addWidget(welcome_label)

        password_label = QLabel("비밀번호 설정:")
        password_label.setStyleSheet("font-size: 10pt; font-family: Arial;")
        main_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("6~14 자리로 설정해 주세요")
        self.password_input.setStyleSheet("font-size: 10pt; font-family: Arial;")
        main_layout.addWidget(self.password_input)

        confirm_password_label = QLabel("비밀번호 확인:")
        confirm_password_label.setStyleSheet("font-size: 10pt; font-family: Arial;")
        main_layout.addWidget(confirm_password_label)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setStyleSheet("font-size: 10pt; font-family: Arial;")
        main_layout.addWidget(self.confirm_password_input)

        # 비밀번호 상태 레이블
        self.password_warning_label = QLabel("")
        self.password_warning_label.setStyleSheet("font-size: 9pt; color: red; font-family: Arial;")
        self.password_warning_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.password_warning_label)

        # 이메일 입력
        email_label = QLabel("이메일:")
        email_label.setStyleSheet("font-size: 10pt; font-family: Arial;")
        main_layout.addWidget(email_label)

        self.email_input = QLineEdit()
        self.email_input.setStyleSheet("font-size: 10pt; font-family: Arial;")
        main_layout.addWidget(self.email_input)

        # 이메일 상태 레이블
        self.email_warning_label = QLabel("")
        self.email_warning_label.setStyleSheet("font-size: 9pt; color: red; font-family: Arial;")
        self.email_warning_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.email_warning_label)

        # 인증 코드 전송 버튼
        self.send_code_button = QPushButton("인증 코드 보내기")
        self.send_code_button.setStyleSheet("font-size: 10pt; font-family: Arial;")
        self.send_code_button.setEnabled(False)
        self.send_code_button.clicked.connect(self.send_verification_code)
        main_layout.addWidget(self.send_code_button)

        # 인증 코드 입력
        verification_code_label = QLabel("인증 코드:")
        verification_code_label.setStyleSheet("font-size: 10pt; font-family: Arial;")
        main_layout.addWidget(verification_code_label)

        self.verification_code_input = QLineEdit()
        self.verification_code_input.setStyleSheet("font-size: 10pt; font-family: Arial;")
        main_layout.addWidget(self.verification_code_input)

        # 타이머 레이블
        self.timer_label = QLabel("")
        self.timer_label.setStyleSheet("font-size: 9pt; color: blue; font-family: Arial;")
        main_layout.addWidget(self.timer_label)

        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        cancel_button = QPushButton("취소")
        cancel_button.setStyleSheet("font-size: 10pt; font-family: Arial;")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)

        self.submit_button = QPushButton("설정")
        self.submit_button.setStyleSheet("font-size: 10pt; font-family: Arial;")
        self.submit_button.setEnabled(False)  # 초기에는 버튼 비활성화
        self.submit_button.clicked.connect(lambda: self.handle_initial_setup(dialog))
        button_layout.addWidget(self.submit_button)

        main_layout.addLayout(button_layout)

        # 입력 필드 변화에 따른 상태 업데이트 연결
        self.password_input.textChanged.connect(self.check_inputs)
        self.confirm_password_input.textChanged.connect(self.check_inputs)
        self.email_input.textChanged.connect(self.check_inputs)
        self.verification_code_input.textChanged.connect(self.check_inputs)

        dialog.setLayout(main_layout)
        dialog.exec_()

    def check_inputs(self):
        # 입력 필드 상태 확인 및 설정 버튼 활성화/비활성화 처리
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        email = self.email_input.text()
        verification_code = self.verification_code_input.text()

        # 비밀번호 조건 확인
        if len(password) < 6 or len(password) > 14:
            self.password_warning_label.setText("* 6~14 자리로 설정해 주세요")
            self.password_warning_label.setStyleSheet("font-size: 9pt; color: red; font-family: Arial;")
        elif password != confirm_password:
            self.password_warning_label.setText("* 비밀번호가 일치하지 않습니다")
            self.password_warning_label.setStyleSheet("font-size: 9pt; color: red; font-family: Arial;")
        else:
            self.password_warning_label.setText("비밀번호가 일치합니다.")
            self.password_warning_label.setStyleSheet("font-size: 9pt; color: green; font-family: Arial;")

        # 이메일 형식 확인
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, email):
            self.email_warning_label.setText("* 이메일 형식을 작성해 주세요")
            self.send_code_button.setEnabled(False)
        else:
            self.email_warning_label.setText("")
            self.send_code_button.setEnabled(True)

        # 모든 필수 입력값이 올바르게 입력되었는지 확인
        if 6 <= len(password) <= 14 and password == confirm_password and re.match(email_pattern, email) and verification_code == self.correct_verification_code:
            self.submit_button.setEnabled(True)
        else:
            self.submit_button.setEnabled(False)

    def handle_initial_setup(self, dialog):
        # 초기 설정 완료 처리
        password = self.password_input.text().encode('utf-8')
        
        # 솔트 생성 및 암호화 저장
        self.salt = os.urandom(16)  # 16 바이트 솔트 생성
        cipher_buffer = (c_ubyte * (len(self.salt) + 16))()
        result = self.salthide.encrypt_message(c_char_p(self.salt), cipher_buffer)
        if result != 0:
            QMessageBox.warning(dialog, "오류", "솔트 암호화에 실패했습니다.")
            return
        encrypted_text = bytes(cipher_buffer)
        with open(os.path.join(os.path.dirname(__file__), "encrypted_data.bin"), "wb") as f:
            f.write(encrypted_text)

        # 비밀번호와 솔트 결합 후 해싱
        hashed_password = (ctypes.c_ubyte * 32)()
        self.hasher.hash_password(password, self.salt, hashed_password)

        # 해시된 비밀번호 저장
        self.password_hash = bytes(hashed_password)
        
        # 이메일 암호화 및 저장 (수정된 부분)
        email_data = self.email_input.text().encode('utf-8')
        email_buffer = (c_ubyte * (len(email_data) + 16))()
        result = self.salthide.encrypt_message(c_char_p(email_data), email_buffer)
        if result != 0:
            QMessageBox.warning(dialog, "오류", "이메일 암호화에 실패했습니다.")
            return
        self.email = bytes(email_buffer).hex()  # JSON에 저장할 수 있도록 hex 형식으로 변환

        # 초기 설정 완료
        self.setup = True
        self.save_config()  # 설정 저장
        self.load_config() 
        self.load_key()
        TaskRunner.run(self.encrypt,self.secure_folder_path)
        #QMessageBox.information(dialog, "비번:"+self.password_hash)


        QMessageBox.information(dialog, "설정 완료", "초기 설정이 완료되었습니다.")
        dialog.accept()

    #################################################초기설정↑↑↑↑

    #################################################이메일전송↓↓↓↓
    # 인증 코드 보내기 메소드 추가됨
    def send_verification_code(self):
        try:
            smtp_server = "smtp.gmail.com"  # SMTP 서버 주소
            smtp_port = 587  # SMTP 포트 번호
            smtp_user = "neoclick04@gmail.com"  # 보내는 이메일 주소
            smtp_password = "ldkf yfoa oznz cchp"  # 이메일 비밀번호
            timerset=False
            if self.email == None:
                timerset=True
                recipient_email = self.email_input.text()
            else:
                recipient_email=self.email
            
            progress_dialog = QProgressDialog(None)  # 부모를 None으로 설정
            progress_dialog.setWindowTitle("잠시만 기다려주세요")
            progress_dialog.setLabelText("인증 코드를 보내는 중입니다...")
            progress_dialog.setFixedSize(300, 100)  # 창 크기 조정
            progress_dialog.setWindowModality(Qt.ApplicationModal)  # 창이 닫힐 때까지 다른 작업 불가
            progress_dialog.setMinimumDuration(0)  # 즉시 창 표시
            progress_dialog.setCancelButton(None)  # 취소 버튼 제거
            progress_dialog.show()

            self.correct_verification_code = str(random.randint(100000, 999999))  # 인증 코드 생성

            msg = MIMEText(f"인증 코드: {self.correct_verification_code}")
            msg['Subject'] = "보안 폴더 인증 코드"
            msg['From'] = smtp_user
            msg['To'] = recipient_email
           
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, recipient_email, msg.as_string())
                server.quit()  # 명시적으로 서버 연결 종료
            progress_dialog.close()  # 대기창 닫기
            QMessageBox.information(None, "인증 코드 전송", "인증 코드가 전송되었습니다.")
            if(timerset==True):
                self.start_timer()
        except Exception as e:
            QMessageBox.warning(None, "오류", f"인증 코드를 보내는 중 오류가 발생했습니다: {e}")

    def start_timer(self):
        # 타이머 시작 (3분 제한)
        self.remaining_time = 180  # 3분
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # 1초마다 업데이트
        self.update_timer()  # 초기 업데이트

    def update_timer(self):
        if self.remaining_time > 0:
            minutes, seconds = divmod(self.remaining_time, 60)
            self.timer_label.setText(f"인증 코드 만료까지 남은 시간: {minutes:02d}:{seconds:02d}")
            self.remaining_time -= 1
        else:
            self.timer.stop()
            self.timer_label.setText("인증 코드가 만료되었습니다. 다시 시도해 주세요.")
            self.correct_verification_code = None
    #################################################이메일전송↑↑↑↑

    #################################################설정값저장↓↓↓↓
    #설정 정보를 파일에서 불러오는 함수
    def load_config(self):
        # 저장된 암호문(솔트) 불러오기 및 복호화
        if os.path.exists(os.path.join(os.path.dirname(__file__), "encrypted_data.bin")):
            with open(os.path.join(os.path.dirname(__file__), "encrypted_data.bin"), "rb") as f:
                loaded_ciphertext = f.read()
            loaded_ciphertext_length = len(loaded_ciphertext)
            loaded_ciphertext_buffer = (c_ubyte * loaded_ciphertext_length).from_buffer_copy(loaded_ciphertext)
            decrypted_buffer = (c_ubyte * (loaded_ciphertext_length - 16))()
            result_decrypt = self.salthide.decrypt_message(loaded_ciphertext_buffer, decrypted_buffer, loaded_ciphertext_length)
            if result_decrypt != 0:
                raise ValueError("솔트 복호화에 실패했습니다.")
            self.salt = bytes(decrypted_buffer)

        # JSON 파일에서 설정 불러오기
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as file:
                config = json.load(file)
                self.setup = config.get("setup", False)
                self.password_hash = bytes.fromhex(config.get("password_hash", "")) if config.get("password_hash") else None
                
                # 이메일 복호화 (수정된 부분)
                if config.get("email"):
                    encrypted_email = bytes.fromhex(config["email"])  # hex 형식의 암호화된 이메일 불러오기
                    encrypted_email_buffer = (c_ubyte * len(encrypted_email)).from_buffer_copy(encrypted_email)
                    decrypted_email_buffer = (c_ubyte * (len(encrypted_email) - 16))()  # 복호화된 데이터를 담을 버퍼
                    result_decrypt = self.salthide.decrypt_message(encrypted_email_buffer, decrypted_email_buffer, len(encrypted_email))
                    if result_decrypt != 0:
                        raise ValueError("이메일 복호화에 실패했습니다.")
                    self.email = bytes(decrypted_email_buffer).decode('utf-8')  # 복호화된 이메일을 평문으로 변환
                else:
                    self.email = None

    
    #설정 정보를 파일에 저장하는 함수
    def save_config(self):
        config = {
            "setup": self.setup,
            "password_hash": self.password_hash.hex() if self.password_hash else None,
            "email": self.email
        }
        with open(self.config_file, "w") as file:
            json.dump(config, file)

    def authenticate_user(self, password):
        """입력한 비밀번호가 저장된 해시와 일치하는지 확인"""
        if not self.salt:
            return False

        hashed_password = (ctypes.c_ubyte * 32)()
        self.hasher.hash_password(password.encode('utf-8'), self.salt, hashed_password)
        
        # 저장된 해시와 비교하여 인증 결과 반환
        return bytes(hashed_password) == self.password_hash
    #################################################설정값저장↑↑↑↑

    #################################################RESET↓↓↓↓
    def reset(self, parent=None):
    # 커스텀 대화창
        dialog = QDialog(parent)
        dialog.setWindowTitle("비밀번호 초기화 - 주의사항")

        # 주의사항 메시지
        message = (
    "<p style='font-size:16px;'>설정을 초기화하시겠습니까?</p>"
    "<p style='color:red; font-weight:bold; font-size:20px; text-align:center;'>※ 주의사항 ※</p>"
    "<ul style='font-size:16px; color:black; line-height:1.5;'>"
    "<li>초기화 과정에서 암호키가 삭제되므로 보안폴더 내 모든 파일이 복호화됩니다.</li>"
    "<li>복호화된 파일은 외부에 노출될 가능성이 있습니다.</li>"
    "<li>파일 수가 많을수록 복호화 시간이 길어질 수 있고 오작동 날수있습니다.</li>"
    "<li><b><u>파일을 해제하고 초기화하는것을 추천합니다.(파일깨져도 책임안짐)</li>"
    "</ul>"
    "<p style='font-size:16px; color:black;'>"
    "초기화 후 보안을 유지하려면 반드시 새로운 비밀번호를 설정해 주세요."
    "</p>"
)


        label = QLabel(message)
        label.setWordWrap(True)

        # 체크박스
        checkbox = QCheckBox("주의사항을 읽었으며 이해했습니다.")
        checkbox.setChecked(False)

        # 버튼
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_button = buttons.button(QDialogButtonBox.Ok)
        ok_button.setEnabled(False)  # 초기에는 확인 버튼 비활성화
        buttons.rejected.connect(dialog.reject)
        buttons.accepted.connect(dialog.accept)

        # 체크박스 상태에 따라 확인 버튼 활성화/비활성화
        checkbox.stateChanged.connect(lambda state: ok_button.setEnabled(state == Qt.Checked))

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(checkbox)
        layout.addWidget(buttons)
        dialog.setLayout(layout)

        # 대화창 실행
        if dialog.exec_() == QDialog.Accepted:
            try:
                TaskRunner.run(self.decrypt,self.secure_folder_path)
                # 설정 파일 삭제
                if os.path.exists(self.config_file):
                    os.remove(self.config_file)

                # 암호화된 데이터 파일 삭제
                encrypted_data_path = os.path.join(os.path.dirname(__file__), "encrypted_data.bin")
                if os.path.exists(encrypted_data_path):
                    os.remove(encrypted_data_path)

                # 모든 관련 변수 초기화
                self._initialized = False
                self.__init__()  # 인스턴스 재초기화

                QMessageBox.information(parent, "초기화 완료", "모든 설정이 초기화되었습니다. 다시 설정을 진행해 주세요.")
                
                # 초기 설정을 다시 진행
                self.set_initial_password(parent)

            except Exception as e:
                QMessageBox.critical(parent, "오류", f"초기화 중 오류가 발생했습니다: {str(e)}")

    #################################################RESET↑↑↑↑

    def load_key(self):
        # password_hash가 None인 경우 바로 종료
        if self.password_hash is None:
            self.AESkey = None
            return  # 함수 종료

        try:
            # AES 키 생성
            hashed_key = (ctypes.c_ubyte * 32)()  # 32바이트 크기의 해시 생성
            self.hasher.hash_password(self.password_hash, self.salt, hashed_key)
            self.AESkey = bytes(hashed_key)
        except Exception as e:
            # 키 생성 실패 시 에러 메시지 표시
            self.AESkey = None
            QMessageBox.critical(None, "Error", f"AES 키 생성에 실패했습니다: {e}")

    
    def encrypt(self, path):
        
        #AESManager의 fast_encrypt_folder 메서드를 호출하여 폴더를 암호화합니다.
        
        if self.AESkey is None:
            raise ValueError("AES 키가 설정되지 않았습니다. 초기화를 먼저 수행하세요.")

        # AESManager를 동적으로 임포트하고 생성
        from .ProcessAES import AESManager
        aes_manager = AESManager()
        aes_manager.pm = self  # AESManager에 PasswordManager 자신을 전달
        aes_manager.encrypt(path)

    def decrypt(self, path):
        #AESManager의 fast_decrypt_folder 메서드를 호출하여 폴더를 복호화합니다.
        if self.AESkey is None:
            raise ValueError("AES 키가 설정되지 않았습니다. 초기화를 먼저 수행하세요.")

        # AESManager를 동적으로 임포트하고 생성
        from .ProcessAES import AESManager
        aes_manager = AESManager()
        aes_manager.pm = self  # AESManager에 PasswordManager 자신을 전달
        aes_manager.decrypt(path)
