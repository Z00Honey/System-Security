import ctypes
import os

# C 라이브러리 로드
lib_path = os.path.join(os.path.dirname(__file__), '../build/libfile_explorer.so')
explorer_lib = ctypes.CDLL(lib_path)

# C 함수 정의
explorer_lib.list_files.argtypes = [ctypes.c_char_p]
explorer_lib.list_files.restype = None

def list_files(directory):
    explorer_lib.list_files(directory.encode('utf-8'))