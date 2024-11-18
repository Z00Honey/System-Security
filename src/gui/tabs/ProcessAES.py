import os
import ctypes
from PyQt5.QtWidgets import QMessageBox
from .password_manager import PasswordManager  # PasswordManager 임포트

class AESManager:
    def __init__(self):
        # AES DLL 로드
        current_directory = os.path.dirname(__file__)
        aes_dll_path = os.path.join(current_directory, 'aes.dll')
        self.AES = ctypes.CDLL(aes_dll_path)

        self.AES.aes_cbc_encrypt.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte)]
        self.AES.aes_cbc_encrypt.restype = ctypes.c_int

        self.AES.aes_cbc_decrypt.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte)]
        self.AES.aes_cbc_decrypt.restype = ctypes.c_int

        # PasswordManager 객체 생성 및 자동 설정 로드
        self.pm = PasswordManager()  # 객체 이름을 짧게 변경

    def enc_data(self, data):
        # 데이터 암호화
        if self.pm.AESkey is None:
            raise ValueError("AES 키가 설정되지 않았습니다.")
        key = self.pm.AESkey
        encrypted = (ctypes.c_ubyte * (len(data) + 16))()  # IV(16바이트) + 암호문
        key_c = (ctypes.c_ubyte * len(key)).from_buffer_copy(key)
        input_data = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)

        result = self.AES.aes_cbc_encrypt(key_c, input_data, len(data), encrypted)
        if result != 0:
            raise RuntimeError("Encryption failed")
        return bytes(encrypted)

    def dec_data(self, data):
        # 데이터 복호화
        if self.pm.AESkey is None:
            raise ValueError("AES 키가 설정되지 않았습니다.")
        key = self.pm.AESkey
        decrypted = (ctypes.c_ubyte * (len(data) - 16))()  # 암호문에서 IV 제거
        key_c = (ctypes.c_ubyte * len(key)).from_buffer_copy(key)
        input_data = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)

        result = self.AES.aes_cbc_decrypt(key_c, input_data, len(data), decrypted)
        if result != 0:
            raise RuntimeError("Decryption failed")
        return bytes(decrypted)

    def enc_file(self, path):
        # 파일 암호화
        with open(path, 'rb+') as f:
            data = f.read()
            pad_len = 16 - (len(data) % 16)  # PKCS7 패딩 추가
            data += bytes([pad_len] * pad_len)
            encrypted = self.enc_data(data)
            f.seek(0)
            f.truncate()
            f.write(encrypted)

    def dec_file(self, path):
        # 파일 복호화
        with open(path, 'rb+') as f:
            data = f.read()
            decrypted_padded = self.dec_data(data)
            pad_len = decrypted_padded[-1]
            decrypted = decrypted_padded[:-pad_len]  # 패딩 제거
            f.seek(0)
            f.truncate()
            f.write(decrypted)

    def enc_folder(self, path):
        # 폴더 내 모든 파일 암호화
        for root, _, files in os.walk(path):
            for file in files:
                self.enc_file(os.path.join(root, file))

    def dec_folder(self, path):
        # 폴더 내 모든 파일 복호화
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    self.dec_file(os.path.join(root, file))

                # 빈 폴더 처리
                if not files and not dirs:
                    print(f"빈 폴더 처리: {root}")  # 디버그 메시지
                    continue  # 빈 폴더는 복호화 작업이 필요 없음
        except Exception as e:
            QMessageBox.critical(None, "복호화 오류", f"빈 폴더 처리 중 오류 발생: {e}")

    def encrypt(self, path):
        # 경로를 자동으로 판단하여 파일 또는 폴더 암호화
        try:
            if not os.path.exists(path):
                QMessageBox.warning(None, "경고", "암호화할 파일이나 폴더가 존재하지 않습니다.")
                return

            if os.path.isdir(path):
                self.enc_folder(path)
            elif os.path.isfile(path):
                self.enc_file(path)
            else:
                QMessageBox.warning(None, "경고", f"유효하지 않은 경로입니다: {path}")
        except Exception as e:
            QMessageBox.critical(None, "암호화 오류", f"암호화 작업 중 오류 발생: {e}")

    def decrypt(self, path):
        # 경로를 자동으로 판단하여 파일 또는 폴더 복호화
        try:
            if not os.path.exists(path):
                QMessageBox.warning(None, "경고", "복호화할 파일이나 폴더가 존재하지 않습니다.")
                return

            if os.path.isdir(path):
                self.dec_folder(path)
            elif os.path.isfile(path):
                self.dec_file(path)
            else:
                QMessageBox.warning(None, "경고", f"유효하지 않은 경로입니다: {path}")
        except Exception as e:
            QMessageBox.critical(None, "복호화 오류", f"복호화 작업 중 오류 발생: {e}")
