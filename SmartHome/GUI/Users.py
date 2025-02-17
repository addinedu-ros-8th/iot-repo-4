import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import Qt
import mysql.connector

from_class = uic.loadUiType("Users.ui")[0]

class WindowClass(QMainWindow, from_class):
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

        self.btnSearch.clicked.connect(self.searchUser)

    def searchUser(self):
        params = ""

        name = self.editName.text()

        if name != "":
            params = "WHERE name = " + name

        cursor = self.remote.cursor()
        cursor.execute(f"SELECT * FROM users {params}")
        results = cursor.fetchall()
        
        for result in results:
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)

            checkbox = QCheckBox()
            widget = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignCenter)  # 체크박스를 가운데 정렬
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)
            self.tableWidget.setCellWidget(row, 0, widget)

            # 사용자 정보 추가
            self.tableWidget.setItem(row, 1, QTableWidgetItem(str(result[1])))  # name
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(result[2])))  # id
            self.tableWidget.setItem(row, 3, QTableWidgetItem(str(result[3])))  # name
            self.tableWidget.setItem(row, 4, QTableWidgetItem(str(result[4])))  # birthday
            self.tableWidget.setItem(row, 5, QTableWidgetItem(str(result[5])))  # phone
            self.tableWidget.setItem(row, 6, QTableWidgetItem(str(result[6])))  # level
            self.tableWidget.setItem(row, 7, QTableWidgetItem(str(result[7])))  # createDate
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindows = WindowClass()
    mywindows.show()

    sys.exit(app.exec_())