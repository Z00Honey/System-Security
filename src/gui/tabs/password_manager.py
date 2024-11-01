from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QApplication
from PyQt5.QtCore import Qt, QTimer
import re
import sys
import smtplib
import random
from email.mime.text import MIMEText

class PasswordManager:
    def __init__(self):
        self.setup = False
        self.password = None
        self.email = None
        self.correct_verification_code = 111111
        self.timer = None
        self.remaining_time = 0

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

    # 인증 코드 보내기 메소드 추가됨
    def send_verification_code(self):
        try:
            smtp_server = "smtp.gmail.com"  # SMTP 서버 주소
            smtp_port = 587  # SMTP 포트 번호
            smtp_user = "neoclick04@gmail.com"  # 보내는 이메일 주소
            smtp_password = "ldkf yfoa oznz cchp"  # 이메일 비밀번호

            recipient_email = self.email_input.text()
            self.correct_verification_code = str(random.randint(100000, 999999))  # 인증 코드 생성

            msg = MIMEText(f"인증 코드: {self.correct_verification_code}")
            msg['Subject'] = "보안 폴더 인증 코드"
            msg['From'] = smtp_user
            msg['To'] = recipient_email

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, recipient_email, msg.as_string())

            QMessageBox.information(None, "인증 코드 전송", "인증 코드가 전송되었습니다.")
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

    def check_inputs(self):
        # 입력 필드 상태 확인 및 설정 버튼 활성화/비활성화 처리
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        email = self.email_input.text()
        verification_code = self.verification_code_input.text()

        # 비밀번호 조건 확인
        if len(password) < 6 or len(password) > 14:
            self.password_warning_label.setText("* 6~14 자리로 설정해 주세요")
        elif password != confirm_password:
            self.password_warning_label.setText("* 비밀번호가 일치하지 않습니다")
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
        self.password = self.password_input.text()
        self.email = self.email_input.text()
        self.setup=True
        QMessageBox.information(dialog, "설정 완료", "초기 설정이 완료되었습니다.")
        dialog.accept()


