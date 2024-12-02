from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSizePolicy, QMenu,
    QAction, QMessageBox, QProgressDialog,
    QLineEdit
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize
from utils.load import load_stylesheet, image_base_path
from utils.analysis import analyze_file
from utils.virus_scan import VirusScanThread
from dotenv import load_dotenv
import os
from utils.secure import TaskRunner

class RenameLineEdit(QLineEdit):
    """
    QLineEdit를 상속받는 클래스
    """
    def __init__(self, old_name, parent=None):
        super().__init__(old_name, parent)
        self.old_name = old_name

    def focusOutEvent(self, event):
        self.setText(self.old_name)
        super().focusOutEvent(event)

class ToolBar(QWidget):
    """
    파일 작업 및 보안 검사를 위한 버튼들을 포함한 툴바 위젯입니다.
    """
    
    def show_message_with_icon(self, title: str, text: str, icon_filename: str) -> None:
        """
        사용자 정의 아이콘을 사용한 메시지 박스를 표시합니다.

        Args:
            title (str): 메시지 박스 제목.
            text (str): 메시지 내용.
            icon_filename (str): 사용자 정의 아이콘 파일 이름.
        """
        message_box = QMessageBox(self)
        message_box.setWindowTitle(title)
        message_box.setText(text)

     
        custom_icon_path = image_base_path(icon_filename)
        custom_icon = QPixmap(custom_icon_path)
        message_box.setIconPixmap(custom_icon)

        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.setStandardButtons(QMessageBox.NoButton)  

        ok_button = message_box.addButton("확인", QMessageBox.AcceptRole)
        message_box.exec_()


    def image_base_path(file_name: str) -> str:
        """
        주어진 파일 이름에 대한 전체 경로를 반환합니다.

        Args:
            file_name (str): 파일 이름 (예: 'shield.png').

        Returns:
            str: 파일의 전체 경로.
        """
        base_path = os.path.join(os.path.dirname(__file__), "assets/images")
        return os.path.join(base_path, file_name)


    def __init__(self, parent: QWidget = None, secure_manager=None) -> None:
        """
        ToolBar 위젯을 초기화합니다.

        Args:
            parent (QWidget, optional): 부모 위젯입니다. 기본값은 None입니다.
            secure_manager (optional): 보안 폴더 관리 객체입니다.
        """
        super().__init__(parent)
        self.parent = parent
        self.secure_manager = secure_manager  # 보안 객체 저장

        # .env 파일에서 환경 변수를 로드합니다.
        load_dotenv()

        self.setObjectName("tool_bar")
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.create_toolbar_buttons()
        self.setLayout(self.layout)
        self.setStyleSheet(load_stylesheet("tool_bar.css"))

        self.setFixedHeight(40)  # 툴바 높이 설정
        self.setFixedWidth(1000)  # 툴바 너비 설정 (필요에 따라 조정)
        self.inline_widget = None

    def create_toolbar_buttons(self) -> None:
        """
        툴바 버튼들을 생성하고 레이아웃에 추가합니다.
        """
        button_info = [
            {"name": "new_folder", "icon": "new_folder.png"},
            {"name": "cut", "icon": "cut.png"},
            {"name": "copy", "icon": "copy.png"},
            {"name": "paste", "icon": "paste.png"},
            {"name": "rename", "icon": "rename.png"},
            {"name": "delete", "icon": "delete.png"},
            {"name": "shield", "icon": "shield.png", "menu": True},
            {"name": "lock", "icon": "lock.png"},  # 잠금 해제 버튼 추가
        ]

        for info in button_info:
            button = QPushButton()
            button.setIcon(QIcon(image_base_path(info["icon"])))
            button.setIconSize(self.get_icon_size(info["name"]))
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            self.layout.addWidget(button)

            if info["name"] == "new_folder":
                button.clicked.connect(self.start_new_folder)

            if info["name"] in ["copy", "paste", "cut"]:
                event = getattr(self, f'file_{info["name"]}')
                button.clicked.connect(event)

            if info.get("menu") and info["name"] == "shield":
                menu = self.create_shield_menu()
                button.setMenu(menu)

            # 잠금 버튼의 이벤트 처리
            if info["name"] == "lock":
                button.clicked.connect(self.toggle_lock)

            if info["name"] == "rename":
                button.clicked.connect(self.start_rename)

            if info["name"] == "delete":
                button.clicked.connect(self.file_delete)

    def get_icon_size(self, name: str) -> QSize:
        """
        버튼 이름에 따라 적절한 아이콘 크기를 반환합니다.

        Args:
            name (str): 버튼의 이름입니다.

        Returns:
            QSize: 아이콘의 크기입니다.
        """
        if name == "memo":
            return QSize(36, 36)
        elif name == "shield":
            return QSize(32, 32)
        elif name == "lock":
            return QSize(80,80)
        else:
            return QSize(28, 28)

    def toggle_lock(self) -> None:
        """
        잠금/해제 상태를 토글하는 함수입니다.
        self.secure_manager.authenticated 값을 확인하여 
        파일이나 폴더의 잠금을 처리합니다.
        """
        main_window = self.window()
        file_list = main_window.file_explorer_bar.file_area.file_list
        current_index = file_list.tree_view.currentIndex()

        if not current_index.isValid():
            self.show_warning_message("경고", "파일 또는 폴더를 선택해주세요.")
            return

        file_path = file_list.model.filePath(current_index)
        
        size_in_bytes = self.get_size(file_path)
        if self.secure_manager.pwd_mgr.AESkey is None:  # None으로 체크
            QMessageBox.warning(self, "Error", "AES 키가 설정되지 않았습니다.")
            return  # 키가 없으면 더 이상 실행하지 않음
        
        size_limit = 5 * 1024**3  # 5GB
        if size_in_bytes > size_limit:
            QMessageBox.warning(self, "Error", "파일 또는 폴더 크기가 5GB를 초과하여 작업을 수행할 수 없습니다.")
            return  # 크기 초과 시 실행 중단

        # 인증 여부 확인
        if not self.secure_manager.authenticated:
            # 잠금 메시지창
            reply = QMessageBox.question(
                self, "잠금", "해당 폴더(파일)를 잠금 처리 하시겠습니까?",
                QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                try:
                    TaskRunner.run(self.secure_manager.lock, file_path)
                    QMessageBox.information(self, "잠금 완료", "폴더(파일)가 성공적으로 잠금 처리되었습니다.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"잠금 중 오류 발생: {str(e)}")
        else:
            # 해제 메시지창
            reply = QMessageBox.question(
                self, "해제", "해당 폴더(파일)를 잠금 해제 하시겠습니까?",
                QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                try:
                    TaskRunner.run(self.secure_manager.unlock, file_path)
                    QMessageBox.information(self, "해제 완료", "폴더(파일)가 성공적으로 잠금 해제되었습니다.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"해제 중 오류 발생: {str(e)}")


    def create_shield_menu(self) -> QMenu:
        """
        보안 검사를 위한 메뉴를 생성합니다.

        Returns:
            QMenu: 생성된 메뉴입니다.
        """
        menu = QMenu()
        extension_action = QAction("확장자 검사", menu)
        virus_action = QAction("바이러스 검사", menu)

        extension_action.triggered.connect(self.run_extension_check)
        virus_action.triggered.connect(self.run_virus_check)

        menu.addAction(extension_action)
        menu.addAction(virus_action)

        return menu
    

    def file_copy(self) -> None:
        """복사 작업을 처리합니다."""
        self.parent.file_event('copy')

    def file_cut(self) -> None:
        """잘라내기 작업을 처리합니다.""" 
        self.parent.file_event('cut')

    def file_paste(self) -> None:
        """붙여넣기 작업을 처리합니다.""" 
        self.parent.file_event('paste')

    def start_new_folder(self) -> None:
        """
        선택된 폳더 안에 새로운 폴더를 생성.
        """
        main_window = self.window()
        file_list = main_window.file_explorer_bar.file_area.file_list
        current_index = file_list.tree_view.currentIndex()
        
        if current_index.isValid():
            parent_index = current_index if file_list.model.isDir(current_index) else current_index.parent()
        else:
            parent_index = file_list.tree_view.rootIndex()

        new_folder_index = file_list.model.mkdir(parent_index, "새 폴더")
        if new_folder_index.isValid():
            file_list.tree_view.setCurrentIndex(new_folder_index)
            self.start_rename(new_folder_index)

    def start_rename(self, index=None) -> None:
        """
        선택된 파일 이름을 바꿉니다.
        """
        main_window = self.window()
        file_list = main_window.file_explorer_bar.file_area.file_list
        if index is None:
            index = file_list.tree_view.currentIndex()
        if not index.isValid():
            return

        self.remove_inline_widget()
        old_name = file_list.model.fileName(index)
    
        self.inline_widget = RenameLineEdit(old_name)
        self.inline_widget.setFixedWidth(200)
        self.inline_widget.returnPressed.connect(lambda: self.finish_rename(index))
        self.inline_widget.editingFinished.connect(self.remove_inline_widget)
    
        file_list.tree_view.setIndexWidget(index, self.inline_widget)
        self.inline_widget.setFocus()

    def finish_rename(self, index) -> None:
        main_window = self.window()
        new_name = self.inline_widget.text()
        if new_name:
            model = main_window.file_explorer_bar.file_area.file_list.tree_view.model()
            old_path = model.filePath(index)
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            try:
                os.rename(old_path, new_path)
                model.setRootPath(model.rootPath())
            except OSError as e:
                self.show_error_message("오류", f"이름 변경 중 오류가 발생했습니다: {str(e)}")
        self.remove_inline_widget()

    def remove_inline_widget(self):
        if self.inline_widget:
            main_window = self.window()
            main_window.file_explorer_bar.file_area.file_list.tree_view.setIndexWidget(main_window.file_explorer_bar.file_area.file_list.tree_view.currentIndex(), None)
            self.inline_widget = None

    def file_delete(self) -> None:
        """
        선택된 파일 삭제합니다.
        """
        main_window = self.window()
        file_list = main_window.file_explorer_bar.file_area.file_list
        current_index = file_list.tree_view.currentIndex()
        
        if not current_index.isValid():
            self.show_warning_message("경고", "삭제할 파일 또는 폴더를 선택해주세요.")
            return
        
        file_path = file_list.model.filePath(current_index)
        is_dir = os.path.isdir(file_path)

        message_box = QMessageBox(self)
        message_box.setWindowTitle("삭제 확인")
        message_box.setText(f"선택한 {'폴더' if is_dir else '파일'}을 삭제하시겠습니까?")
        
        delete_icon_path = image_base_path("delete.png")
        delete_icon = QPixmap(delete_icon_path)
        message_box.setIconPixmap(delete_icon)
        
        message_box.setStandardButtons(QMessageBox.NoButton)
        yes_button = message_box.addButton("예", QMessageBox.YesRole)
        no_button = message_box.addButton("아니요", QMessageBox.NoRole)

        message_box.exec_()
        if message_box.clickedButton() == yes_button:
            try:
                if is_dir:
                    import shutil
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                
                file_list.model.setRootPath(file_list.model.rootPath())

                self.show_message_with_icon("삭제 완료", f"선택한 {'폴더' if is_dir else '파일'}이 성공적으로 삭제되었습니다.", "delete.png")
            except OSError as e:
                self.show_error_message("오류", f"삭제 중 오류가 발생했습니다: {str(e)}")
        else:
            self.show_message_with_icon("취소", "삭제 작업이 취소되었습니다.", "delete.png")

    def run_extension_check(self) -> None:
        """
        선택된 파일에 대해 확장자 검사를 실행합니다.
        """
        main_window = self.window()

        file_list = main_window.file_explorer_bar.file_area.file_list
        current_index = file_list.tree_view.currentIndex()
        if not current_index.isValid():
            self.show_warning_message("경고", "파일을 선택해주세요.")
            return

        file_path = file_list.model.filePath(current_index)

        if file_list.model.isDir(current_index):
            self.show_warning_message("경고", "파일만 검사할 수 있습니다.")
            return

        if self.confirm_action("확장자 검사", "선택한 파일에 대한 포맷 및 확장자 불일치 검사를 진행하시겠습니까?"):
            result = analyze_file(file_path)
            self.show_message_with_icon("확장자 검사 결과", result, "shield.png")

    def run_virus_check(self) -> None:
        """
        선택된 파일 또는 폴더에 대해 바이러스 검사를 실행합니다.
        """
        main_window = self.window()
        file_list = main_window.file_explorer_bar.file_area.file_list
        current_index = file_list.tree_view.currentIndex()

        if not current_index.isValid():
            self.show_warning_message("경고", "파일이나 폴더를 선택해주세요.")
            return

        path = file_list.model.filePath(current_index)

        if file_list.model.isDir(current_index):
            
            folder_content = os.listdir(path)
            files_only = [f for f in folder_content if os.path.isfile(os.path.join(path, f))]

            if not files_only:
                self.show_info_message("정보", "선택한 폴더에 파일이 없습니다.")
                return

        if self.confirm_action("바이러스 검사", "선택한 파일/폴더에 대한 바이러스 검사를 진행하시겠습니까?"):
            self.start_virus_scan(path)

    def start_virus_scan(self, path: str) -> None:
        """
        바이러스 검사를 시작합니다.

        Args:
            path (str): 검사할 파일 또는 폴더의 경로입니다.
        """
        self.progress_dialog = QProgressDialog("검사 중...", "취소", 0, 100, self)
        self.progress_dialog.setWindowTitle("바이러스 검사")
        self.progress_dialog.setWindowModality(True)

        self.scan_thread = VirusScanThread(path)
        self.scan_thread.finished.connect(self.on_scan_finished)
        self.scan_thread.error.connect(self.on_scan_error)
        self.scan_thread.progress.connect(self.update_progress)

        self.progress_dialog.canceled.connect(self.scan_thread.terminate)
        self.scan_thread.start()
        self.progress_dialog.show()

    def update_progress(self, current: int, total: int) -> None:
        """
        검사 진행 상황을 업데이트합니다.

        Args:
            current (int): 현재 진행 상황입니다.
            total (int): 총 진행 상황입니다.
        """
        if self.progress_dialog:
            progress = int((current / total) * 100)
            self.progress_dialog.setValue(progress)
            self.progress_dialog.setLabelText(f"검사 중... ({current}/{total})")

    def on_scan_finished(self, result: str) -> None:
        """
        바이러스 검사가 완료되었을 때 호출됩니다.

        Args:
            result (str): 검사 결과 메시지입니다.
        """
        self.progress_dialog.close()
        self.show_message_with_icon("검사 완료", result,"shield.png")       
         
    def on_scan_error(self, error_message: str) -> None:
        """
        바이러스 검사 중 오류가 발생했을 때 호출됩니다.

        Args:
            error_message (str): 오류 메시지입니다.
        """
        self.progress_dialog.close()
        self.show_error_message("오류", f"검사 중 오류가 발생했습니다:\n{error_message}")

    def show_warning_message(self, title: str, text: str) -> None:
        """
        경고 메시지 박스를 표시합니다.

        Args:
            title (str): 메시지 박스 제목입니다.
            text (str): 메시지 내용입니다.
        """
        QMessageBox.warning(self, title, text)

    def show_info_message(self, title: str, text: str) -> None:
        """
        정보 메시지 박스를 표시합니다.

        Args:
            title (str): 메시지 박스 제목입니다.
            text (str): 메시지 내용입니다.
        """
        QMessageBox.information(self, title, text)

    def show_error_message(self, title: str, text: str) -> None:
        """
        오류 메시지 박스를 표시합니다.

        Args:
            title (str): 메시지 박스 제목입니다.
            text (str): 메시지 내용입니다.
        """
        QMessageBox.critical(self, title, text)

    def confirm_action(self, title: str, text: str, use_custom_icon: bool = True) -> bool:
        """
        사용자에게 작업 확인 대화 상자를 표시하며, 아이콘 변경 여부를 선택할 수 있습니다.

        Args:
            title (str): 대화 상자 제목입니다.
            text (str): 대화 상자 내용입니다.
            use_custom_icon (bool): True일 경우 사용자 정의 아이콘을 설정합니다.

        Returns:
            bool: 사용자가 '예'를 선택하면 True를 반환합니다.
        """
        message_box = QMessageBox(self)
        message_box.setWindowTitle(title)
        message_box.setText(text)

        if use_custom_icon:
            custom_icon_path = image_base_path("shield.png")
            custom_icon = QPixmap(custom_icon_path)
            message_box.setIconPixmap(custom_icon)

        message_box.setStandardButtons(QMessageBox.NoButton)
        yes_button = message_box.addButton("예", QMessageBox.YesRole)
        no_button = message_box.addButton("아니요", QMessageBox.NoRole)

        message_box.exec_()
        return message_box.clickedButton() == yes_button




    def get_size(self,path):
        """파일 또는 폴더 크기를 계산"""
        if os.path.isfile(path):
            return os.path.getsize(path)  
        elif os.path.isdir(path):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if not os.path.islink(file_path):
                        total_size += os.path.getsize(file_path)
            return total_size  
        else:
            raise ValueError(f"Invalid path: {path} is neither a file nor a folder.")
