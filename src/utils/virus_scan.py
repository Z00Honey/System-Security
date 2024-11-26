from ctypes import cdll, c_char_p, c_bool, c_size_t, create_string_buffer
from PyQt5.QtCore import QThread, pyqtSignal
import os

class VirusScanThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int, int)  # current, total

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.is_folder = os.path.isdir(path)

    def run(self):
        try:
            if self.is_folder:
                result = scan_folder(self.path, self.progress)
            else:
                result = scan_file(self.path)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

def load_virus_scan_dll():
    # 절대 경로 설정
    dll_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dll', 'vrsapi1.dll')
    
    try:
        print(f"DLL 로드 시도: {dll_path}")
        if os.path.exists(dll_path):
            print(f"파일 존재 확인됨: {dll_path}")
            dll = cdll.LoadLibrary(dll_path)
            print(f"DLL 로드 성공: {dll_path}")
            return dll
        else:
            print(f"파일이 존재하지 않음: {dll_path}")
            raise FileNotFoundError(f"DLL 파일을 찾을 수 없습니다: {dll_path}")
    except Exception as e:
        print(f"DLL 로드 실패: {str(e)}")
        return None

def scan_file(file_path):
    dll = load_virus_scan_dll()
    if not dll:
        return "DLL 로드 실패"

    result_buffer = create_string_buffer(4096)
    file_path_bytes = file_path.encode('utf-8')

    scan_file_func = dll.scan_file_virustotal
    scan_file_func.argtypes = [c_char_p, c_char_p, c_size_t]
    scan_file_func.restype = c_bool

    success = scan_file_func(file_path_bytes, result_buffer, 4096)

    if success:
        result = result_buffer.value.decode('utf-8')
        return simplify_result(file_path, result)
    else:
        error_msg = result_buffer.value.decode('utf-8', errors='replace')
        return f"검사 실패: {error_msg}"

def scan_folder(folder_path, progress_callback=None):
    all_files = [
        os.path.join(root, file)
        for root, _, files in os.walk(folder_path) for file in files
    ]
    
    results = []
    total_files = len(all_files)

    for i, file_path in enumerate(all_files, 1):
        if progress_callback:
            progress_callback.emit(i, total_files)
        
        result = scan_file(file_path)
        results.append(result)

    return "\n\n".join(results)

def simplify_result(file_path, raw_result):
    """검사 결과를 간소화"""
    # raw_result 파싱 로직 구현 필요
    detected_engines = "0/70"  # 실제 결과에서 파싱 필요
    is_safe = "위험 없음" if "0/70" in detected_engines else "위험 있음"
    
    return (
        f"파일 이름: {os.path.basename(file_path)}\n"
        f"탐지된 엔진: {detected_engines}\n"
        f"검사 상태: {is_safe}"
    ) 