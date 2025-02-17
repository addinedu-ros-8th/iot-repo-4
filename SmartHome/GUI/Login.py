import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import uic
import mysql.connector 
from Main import WindowClass  # Main.py의 WindowClass 가져오기

# UI 파일 로드
LoginUI = uic.loadUiType("Login.ui")[0]
MainUi = uic.loadUiType("Main.ui")[0]

class LoginWindow(QMainWindow, LoginUI):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Login.ui 로드
        self.remote = mysql.connector.connect(
            host="database-1.c7iiuw4kenou.ap-northeast-2.rds.amazonaws.com",
            user="chillHome",
            password="addinedu1!",
            database="chillHome"
        )

        # 로그인 버튼 클릭 시 Main.py의 WindowClass 실행
        self.Login_btn.clicked.connect(self.open_main_window)

    def open_main_window(self):
        """ MySQL 로그인 검증 후 Main.py 실행 """
        id = self.lineEdit.text()
        passwd = self.lineEdit_2.text()

        cursor = self.remote.cursor()
        cursor.execute(f"SELECT COUNT(*) as cnt FROM users WHERE id = '{id}' and password = '{passwd}'")
        result = cursor.fetchone()

        if result[0] > 0:
            self.main_window = WindowClass()  # Main.py의 WindowClass 실행
            self.main_window.show()  # Main.ui를 실행
            self.close()  # 현재 로그인 창 닫기
        else:
            QMessageBox.warning(self, '로그인 실패', '아이디 또는 비밀번호가 틀렸습니다. 확인 후 다시 시도해주세요.')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loginWindow = LoginWindow()
    loginWindow.show()
    sys.exit(app.exec_())
