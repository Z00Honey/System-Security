from PyQt5.QtWidgets import QApplication, QProgressDialog, QMessageBox
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
import sys


class TaskRunner:
    class TaskThread(QThread):
        # 오류 및 완료 신호 정의
        error = pyqtSignal(str)  # 작업 중 오류 발생 시 신호
        finished = pyqtSignal()  # 작업 완료 신호

        def __init__(self, task, *args, **kwargs):
            super().__init__()
            self.task = task  # 실행할 작업(함수 객체)
            self.args = args  # 함수 위치 인자
            self.kwargs = kwargs  # 함수 키워드 인자

        def run(self):
            try:
                # 실제 작업 실행
                self.task(*self.args, **self.kwargs)
                self.finished.emit()  # 완료 신호 발생
            except Exception as e:
                # 오류 발생 시 오류 신호 발생
                self.error.emit(str(e))

    @staticmethod
    def run(task, *args, parent=None, **kwargs):
        """작업을 비동기로 실행하고 모달 프로그레스 창을 표시."""
        app = QApplication.instance() or QApplication(sys.argv)

        # 대기창 설정
        progress_dialog = QProgressDialog(parent)
        progress_dialog.setWindowTitle("작업 중")
        progress_dialog.setLabelText("작업을 처리하고 있습니다...")
        progress_dialog.setCancelButton(None)  # 취소 버튼 숨기기
        progress_dialog.setWindowModality(Qt.ApplicationModal if parent is None else Qt.WindowModal)
        progress_dialog.setRange(0, 0)
        progress_dialog.setAutoClose(False)

        # 애니메이션 설정
        dots = ["", ".", "..", "..."]
        current_dot_index = 0

        def update_label():
            nonlocal current_dot_index
            progress_dialog.setLabelText(f"작업을 처리하고 있습니다{dots[current_dot_index]}")
            current_dot_index = (current_dot_index + 1) % len(dots)
            QApplication.processEvents()  # UI 업데이트 강제 실행

        # 타이머 설정
        timer = QTimer()
        timer.timeout.connect(update_label)
        timer.start(500)

        # 작업 스레드 실행
        thread = TaskRunner.TaskThread(task, *args, **kwargs)

        # 작업 완료 처리
        thread.finished.connect(lambda: timer.stop())  # 타이머 중지
        thread.finished.connect(progress_dialog.accept)  # 대기창 닫기

        # 오류 처리
        thread.error.connect(lambda err: QMessageBox.critical(parent, "오류", f"작업 중 오류 발생: {err}"))
        thread.error.connect(lambda: timer.stop())  # 타이머 중지
        thread.error.connect(progress_dialog.reject)  # 대기창 닫기

        # 스레드 시작
        thread.start()

        # 모달 대기창 실행
        progress_dialog.exec_()

        # 스레드 대기
        thread.wait()
        thread.deleteLater()
