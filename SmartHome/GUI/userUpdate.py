import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import QDate, QTimer
import mysql.connector

from_class = uic.loadUiType("userUpdate.ui")[0]

class UserUpdateWindow(QMainWindow, from_class):
    def __init__(self, ids=list()):
        super().__init__()
        self.setupUi(self)
        self.ids = ids

        self.setWindowTitle("Home Chill home")
        self.remote = mysql.connector.connect(
            host = "database-1.c7iiuw4kenou.ap-northeast-2.rds.amazonaws.com",
            port = 3306,
            user = "chillHome",
            password = "addinedu1!",
            database = "chillHome"
        )

        self.loadUser()
        self.btnComplete.clicked.connect(self.updateUser)

    def loadUser(self):
        cursor = self.remote.cursor()
        query = f"SELECT * FROM users WHERE id = '{self.ids[0]}'"
        cursor.execute(query)
        results = cursor.fetchall()[0]
        print(results)
        
        self.editId.setText(results[2])
        self.editName.setText(results[4])
        self.editBirthday.setDate(QDate.fromString(results[5], 'yyyyMMdd'))
        self.editPhone.setText(results[6])
        self.editRfidKey.setText(results[7])

    def updateUser(self):
        passwd = self.editPasswd.text()
        rePasswd = self.editRePasswd.text()
        name = self.editName.text()
        birthday = self.editBirthday.text()
        phone = self.editPhone.text()
        rfidKey = self.editRfidKey.text()

        pattern = "/^(?=.*[a-zA-Z])(?=.*[!@#$%^*+=-])(?=.*[0-9]).{8,15}$/"
        
        if passwd != "" and rePasswd:
            if passwd == "" or re.match(pattern, passwd):
                QMessageBox.warning(self, "Update Users", "비밀번호는 대문자, 소문자, 특수문자 모두 포함하는 8자리 이상 15자리 이하의 비밀번호를 입력해주세요.")
                return
            
            if rePasswd == "" or re.match(pattern, rePasswd) or passwd != rePasswd:
                QMessageBox.warning(self, "Update Users", "비밀번호는 대문자, 소문자, 특수문자 모두 포함하는 8자리 이상 15자리 이하의 비밀번호를 입력해주세요.")
                return
            
            if name == "":
                QMessageBox.warning(self, "Update Users", "이름을 입력해주세요.")
                return
            if birthday == "":
                QMessageBox.warning(self, "Update Users", "생년월일을 입력해주세요.")
                return
            if phone == "":
                QMessageBox.warning(self, "Update Users", "전화번호를 입력해주세요.")
                return
            if rfidKey == "":
                QMessageBox.warning(self, "Update Users", "Rfid Key를 입력해주세요.")
                return
        
        sql = "UPDATE users SET password = %s, name = %s, birthday = %s, phone = %s, rfidKey = %s WHERE id = %s"

        cursor = self.remote.cursor()
        cursor.execute(sql, (passwd, name, birthday, phone, rfidKey, self.ids[0]))
        self.remote.commit()
        cursor.close()

        QMessageBox.information(self, "update Complete", "업데이트 완료했습니다.")

        self.close()


            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindows = UserUpdateWindow()
    mywindows.show()

    sys.exit(app.exec_())