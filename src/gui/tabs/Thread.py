from PyQt5.QtWidgets import QApplication, QProgressDialog, QLabel, QMessageBox
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
import sys

class TaskRunner:
    class TaskThread(QThread):
        error = pyqtSignal(str)  # 오류 발생 신호
        finished = pyqtSignal()  # 작업 완료 신호

        def __init__(self, task, *args, **kwargs):
            super().__init__()
            self.task = task  # 실행할 작업(함수 객체)
            self.args = args  # 함수 위치 인자
            self.kwargs = kwargs  # 함수 키워드 인자

        def run(self):
            try:
                self.task(*self.args, **self.kwargs)  # 작업 실행
                self.finished.emit()  # 작업 완료 신호
            except Exception as e:
                self.error.emit(str(e))  # 오류 발생 신호

    @staticmethod
    def run(task, *args, **kwargs):
        app = QApplication.instance() or QApplication(sys.argv)

        # 대기창 생성
        progress_dialog = QProgressDialog()
        progress_dialog.setWindowTitle("작업 중")
        progress_dialog.setCancelButton(None)  # 취소 버튼 숨기기
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setRange(0, 0)  # 진행률 표시를 비활성화 (진행률 바 숨기기)

        # 상태 표시를 위한 라벨
        label = QLabel("작업 중", progress_dialog)
        progress_dialog.setLabel(label)

        # 점 애니메이션
        dots = ["", ".", "..", "...", "...."]
        current_dot_index = 0

        def update_label():
            nonlocal current_dot_index
            label.setText(f"작업 중{dots[current_dot_index]}")
            current_dot_index = (current_dot_index + 1) % len(dots)

        # QTimer 설정
        timer = QTimer()
        timer.timeout.connect(update_label)
        timer.start(500)

        # 작업 스레드 실행
        thread = TaskRunner.TaskThread(task, *args, **kwargs)
        thread.finished.connect(lambda: timer.stop())  # 완료 시 타이머 중지
        thread.finished.connect(progress_dialog.close)  # 완료 시 대기창 닫기
        thread.error.connect(lambda err: QMessageBox.critical(None, "오류", f"작업 중 오류 발생: {err}"))
        thread.error.connect(lambda: timer.stop())  # 오류 발생 시 타이머 중지
        thread.error.connect(progress_dialog.close)  # 오류 발생 시 대화창 닫기

        # 작업 스레드 실행
        thread.start()
        progress_dialog.exec_()  # 모달 대기창 실행

        # 스레드가 종료될 때까지 대기
        thread.wait()
