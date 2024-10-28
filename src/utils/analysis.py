from ctypes import cdll, c_char_p, create_string_buffer
import os

def load_analysis_dll():
    dll_path = os.path.join(os.getcwd(), "scan", "analysis.dll")
    try:
        analysis_dll = cdll.LoadLibrary(dll_path)
        return analysis_dll
    except Exception as e:
        print(f"DLL 로드 실패: {e}")
        return None

def analyze_file(filename):
    dll = load_analysis_dll()
    if not dll:
        return "DLL 로드 실패"

    # 결과를 저장할 버퍼 생성
    result_buffer = create_string_buffer(1024)
    
    # 파일 분석 함수 호출
    dll.analyze_file.argtypes = [c_char_p, c_char_p, c_int]
    dll.analyze_file.restype = c_int
    
    success = dll.analyze_file(
        filename.encode('utf-8'), 
        result_buffer, 
        len(result_buffer)
    )
    
    if success:
        return result_buffer.value.decode('utf-8')
    else:
        return "파일 분석 실패"
