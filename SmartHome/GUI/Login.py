import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic

# UI 파일 로드
LoginUI = uic.loadUiType("Login.ui")[0]
MainUI = uic.loadUiType("Main.ui")[0]

class MainWindow(QMainWindow, MainUI):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Main.ui 로드

class LoginWindow(QMainWindow, LoginUI):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Login.ui 로드

        # 로그인 버튼 클릭 시 메인 창 열기
        self.Login_btn.clicked.connect(self.open_main_window)

    def open_main_window(self):
        self.main_window = MainWindow()  # MainWindow 인스턴스 생성
        self.main_window.show()  # 메인 윈도우 표시
        self.close()  # 현재 로그인 창 닫기

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loginWindow = LoginWindow()
    loginWindow.show()
    sys.exit(app.exec_())
