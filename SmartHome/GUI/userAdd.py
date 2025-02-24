import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import Qt
import mysql.connector
import re
from faceId import WindowClass

from_class = uic.loadUiType("userAdd.ui")[0]
face_id_ui = uic.loadUiType("faceId.ui")[0]

class UserWindow(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle("Home Chill home")
        self.remote = mysql.connector.connect(
            host = "database-1.c7iiuw4kenou.ap-northeast-2.rds.amazonaws.com",
            port = 3306,
            user = "chillHome",
            password = "addinedu1!",
            database = "chillHome"
        )
        self.idCheckFlag = False

        self.editPasswd.setEchoMode(QLineEdit.Password)
        self.editRePasswd.setEchoMode(QLineEdit.Password)

        self.btnExist.clicked.connect(self.checkId)
        self.btnNext.clicked.connect(self.saveUsers)

    def checkId(self):
        id = self.editId.text()
        if id == "":
            QMessageBox.warning(self, "ID Check", "아이디를 입력해주세요.")
            return
        
        cursor = self.remote.cursor()
        cursor.execute(f"SELECT COUNT(*) as cnt FROM users WHERE id = '{id}'")

        result = cursor.fetchone()

        if result[0] > 0:
            QMessageBox.warning(self, "ID Check", "이미 존재하는 아이디입니다.")
            return
        
        self.idCheckFlag = True
        QMessageBox.information(self, "ID Check", "사용가능한 아이디입니다.")
        return
    
    def saveUsers(self):
        id = self.editId.text()
        passwd = self.editPasswd.text()
        rePasswd = self.editRePasswd.text()
        name = self.editName.text()
        birthday = self.editBirthday.text()
        phone = self.editPhone.text()
        rfidKey = self.editRfidKey.text()

        if not self.idCheckFlag:
            QMessageBox.warning(self, "Save Users", "아이디 중복 체크 완료 후 저장 가능합니다.")
            return
        
        pattern = "/^(?=.*[a-zA-Z])(?=.*[!@#$%^*+=-])(?=.*[0-9]).{8,15}$/"
        
        if passwd == "" or re.match(pattern, passwd):
            QMessageBox.warning(self, "Save Users", "비밀번호는 대문자, 소문자, 특수문자 모두 포함하는 8자리 이상 15자리 이하의 비밀번호를 입력해주세요.")
            return
        
        if rePasswd == "" or re.match(pattern, rePasswd) or passwd != rePasswd:
            QMessageBox.warning(self, "Save Users", "비밀번호는 대문자, 소문자, 특수문자 모두 포함하는 8자리 이상 15자리 이하의 비밀번호를 입력해주세요.")
            return
        
        if name == "":
            QMessageBox.warning(self, "Save Users", "이름을 입력해주세요.")
            return
        if birthday == "":
            QMessageBox.warning(self, "Save Users", "생년월일을 입력해주세요.")
            return
        if phone == "":
            QMessageBox.warning(self, "Save Users", "전화번호를 입력해주세요.")
            return
        if rfidKey == "":
            QMessageBox.warning(self, "Save Users", "Rfid Key를 입력해주세요.")
            return
        
        sql = "INSERT INTO users (homeId, id, password, name, birthday, phone, userUid, createDate) VALUES (1, %s, SHA2(%s, 256), %s, %s, %s, %s, NOW())"

        cursor = self.remote.cursor()
        cursor.execute(sql, (id, passwd, name, birthday, phone, rfidKey))
        self.remote.commit()
        cursor.close()

        self.main_window = WindowClass(cursor.lastrowid)
        self.main_window.show()
        self.close() 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    userwindows = UserWindow()
    userwindows.show()

    sys.exit(app.exec_())