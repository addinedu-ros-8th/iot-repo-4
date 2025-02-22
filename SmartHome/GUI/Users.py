import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import Qt
import mysql.connector
from userAdd import UserWindow
from Users_VehicleInformation import VehicleWindow
from userUpdate import UserUpdateWindow

from_class = uic.loadUiType("Users.ui")[0]
userAddUi = uic.loadUiType("userAdd.ui")[0]
vehicleUi = uic.loadUiType("Users_VehicleInformation.ui")[0]

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

        self.btnSearch.clicked.connect(self.userSearch)

        self.btnUserAdd.clicked.connect(self.userAdd)
        self.btnAddVehicle.clicked.connect(self.vehicleInfo)
        self.btnUserUpdate.clicked.connect(self.userUpdate)
        self.btnUserDelete.clicked.connect(self.userDelete)


    def userSearch(self):
        self.tableWidget.setRowCount(0)

        params = ""

        name = self.editName.text()

        if name != "":
            params = "WHERE name = '" + name + "'"

        cursor = self.remote.cursor()
        cursor.execute(f"SELECT * FROM users {params}")
        results = cursor.fetchall()
        
        for result in results:
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)

            checkbox = QCheckBox()
            checkbox.setChecked(False)
            self.tableWidget.setCellWidget(row, 0, checkbox)

            # 사용자 정보 추가
            self.tableWidget.setItem(row, 1, QTableWidgetItem(str(result[2])))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(result[4])))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(str(result[5])))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(str(result[6])))
            self.tableWidget.setItem(row, 5, QTableWidgetItem(str(result[7])))
            self.tableWidget.setItem(row, 6, QTableWidgetItem(str(result[8])))

    def vehicleInfo(self):
        self.main_window = VehicleWindow()
        self.main_window.show()


    def userAdd(self):
        self.main_window = UserWindow()
        self.main_window.show()

    def userUpdate(self):
        ids = list()

        cursor = self.remote.cursor()
        rowCount = self.tableWidget.rowCount()

        for rowIndex in range(rowCount):
            checkbox = self.tableWidget.cellWidget(rowIndex, 0)
            id = self.tableWidget.item(rowIndex, 1).text()
            if checkbox and checkbox.isChecked():
                ids.append(id)

        if not ids or len(ids) > 1:
            QMessageBox.information(self, "Update users", "수정할 유저는 한개만 선택 가능합니다.")
            return
        
        self.main_window = UserUpdateWindow(ids)
        self.main_window.show()

    def userDelete(self):
        ids = list()

        cursor = self.remote.cursor()
        rowCount = self.tableWidget.rowCount()

        for rowIndex in range(rowCount):
            checkbox = self.tableWidget.cellWidget(rowIndex, 0)
            id = self.tableWidget.item(rowIndex, 1).text()
            if checkbox and checkbox.isChecked():
                ids.append(id)

        if not ids:  # 삭제할 유저가 없으면 종료
            QMessageBox.information(self, "Delete users", "삭제할 유저를 선택하세요.")
            return

        retval = QMessageBox.question(self, 'Delete users', str(len(ids)) + '개의 유저를 삭제하시겠습니까?',
                                QMessageBox.Yes | QMessageBox.No)
        
        if retval == QMessageBox.Yes:
            cursor.execute(f"DELETE FROM users WHERE id IN ({','.join(['%s'] * len(ids))})", ids)
            self.remote.commit()
        else:
            return

        self.userSearch()
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindows = WindowClass()
    mywindows.show()

    sys.exit(app.exec_())