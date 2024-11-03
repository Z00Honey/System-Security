from ctypes import cdll, c_char_p, c_int, create_string_buffer
import os
import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QMessageBox, QFileDialog, QPushButton,
    QVBoxLayout, QWidget, QProgressBar, QLabel, QHBoxLayout
)

# 파일 분석을 위한 Worker 스레드 정의
class AnalyzerThread(QThread):
    # 분석이 완료되었을 때 신호를 보냄
    finished = pyqtSignal(str)
    # 오류가 발생했을 때 신호를 보냄
    error = pyqtSignal(str)

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def run(self):
        try:
            result = analyze_file(self.filename)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

# C DLL을 로드하고 파일을 분석하는 함수
def load_analysis_dll():
    dll_path = os.path.join(os.getcwd(), "build", "analysis.dll")
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
    result_buffer = create_string_buffer(2048)  # 버퍼 크기 증가

    # 파일 분석 함수 호출
    dll.analyze_file.argtypes = [c_char_p, c_char_p, c_int]
    dll.analyze_file.restype = c_int

    # Python 문자열을 UTF-8로 인코딩하여 전달
    filename_bytes = filename.encode('utf-8') if sys.platform.startswith('win') else filename.encode('utf-8')

    success = dll.analyze_file(
        filename_bytes,
        result_buffer,
        len(result_buffer)
    )

    if success:
        try:
            # UTF-8로 디코딩, 오류 발생 시 대체 문자 사용
            decoded_result = result_buffer.value.decode('utf-8', errors='replace')
            print("Decoded Result:", decoded_result)  # 디코딩된 결과 출력 (디버깅용)
            return decoded_result
        except UnicodeDecodeError:
            return "디코딩 오류: UTF-8로 변환할 수 없습니다."
    else:
        return "파일 분석 실패"

def parse_result(result):
    lines = result.splitlines()
    analysis_completed = lines[0].replace("분석 완료: ", "") if len(lines) > 0 else ""
    signature_check = lines[1].replace("시그니처 검사: ", "") if len(lines) > 1 else ""
    hidden_count = lines[2].replace("숨겨진 파일: ", "").replace("개", "") if len(lines) > 2 else ""
    hidden_list = lines[3].replace("숨겨진 파일 목록: ", "") if len(lines) > 3 else ""
    print("Parsed Results:", analysis_completed, signature_check, hidden_count, hidden_list)  # 디버깅용
    return analysis_completed, signature_check, hidden_count, hidden_list

def show_popup(analysis_completed, signature_check, hidden_count, hidden_list):
    # QMessageBox 설정
    msg_box = QMessageBox()
    msg_box.setWindowTitle("파일 분석 결과")
    msg_box.setIcon(QMessageBox.Information)
    
    # 메시지 내용 구성
    message = f"분석 완료: {analysis_completed}\n" \
              f"시그니처 검사: {signature_check}\n" \
              f"숨겨진 파일: {hidden_count}개\n" \
              f"숨겨진 파일 목록: {hidden_list}"
    
    msg_box.setText(message)
    msg_box.exec_()

# 메인 애플리케이션 클래스
class FileAnalyzerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.analyzer_thread = None

    def init_ui(self):
        self.setWindowTitle('파일 분석기')

        layout = QVBoxLayout()

        # 파일 선택 및 분석 버튼
        self.button = QPushButton('파일 선택 및 분석')
        self.button.clicked.connect(self.select_and_analyze)
        layout.addWidget(self.button)

        # 진행 표시줄
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 무한 진행 표시
        self.progress_bar.setVisible(False)  # 초기에는 숨김
        layout.addWidget(self.progress_bar)

        # 상태 레이블
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.setGeometry(100, 100, 400, 150)

    def select_and_analyze(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "분석할 파일 선택",
            "",
            "모든 파일 (*)",
            options=options
        )
        if file_path:
            self.status_label.setText(f"분석 중: {file_path}")
            self.progress_bar.setVisible(True)
            self.button.setEnabled(False)  # 버튼 비활성화

            # 분석 스레드 시작
            self.analyzer_thread = AnalyzerThread(file_path)
            self.analyzer_thread.finished.connect(self.on_analysis_finished)
            self.analyzer_thread.error.connect(self.on_analysis_error)
            self.analyzer_thread.start()

    def on_analysis_finished(self, result):
        self.progress_bar.setVisible(False)
        self.button.setEnabled(True)
        self.status_label.setText("분석 완료")
        analysis_completed, signature_check, hidden_count, hidden_list = parse_result(result)
        show_popup(analysis_completed, signature_check, hidden_count, hidden_list)

    def on_analysis_error(self, error_message):
        self.progress_bar.setVisible(False)
        self.button.setEnabled(True)
        self.status_label.setText("분석 실패")
        # 오류 메시지 팝업 표시
        msg_box = QMessageBox()
        msg_box.setWindowTitle("파일 분석 오류")
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(error_message)
        msg_box.exec_()

def main():
    app = QApplication(sys.argv)
    analyzer = FileAnalyzerApp()
    analyzer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
