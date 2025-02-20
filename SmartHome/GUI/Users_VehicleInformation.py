'''
차량 정보 조회 ui의 py 파일입니다.
현재 디비 테이블로 연동과 add 버튼 완성하였습니다.

일차원적인 수정과 삭제 기능을 완료하였습니다.
예외처리는 하지 않아서 다음에 다시 구현하겠습니다 ~
'''

import sys
from PyQt5.QtWidgets import * #QApplication, QMainWindow, QCheckBox, QTableWidgetItem, QHBoxLayout, QWidget, QDialog, QInputDialog, QMessageBox
from PyQt5 import uic, QtWidgets
import mysql.connector
from PyQt5.QtCore import Qt

# load UI file
src = uic.loadUiType("/Users/jane/Desktop/dev/Project/iot-repo-4/SmartHome/GUI/Users_VehicleInformation.ui")[0]

class WindowClass(QMainWindow, src):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Login.ui 로드
        self.remote = mysql.connector.connect(
            host="database-1.c7iiuw4kenou.ap-northeast-2.rds.amazonaws.com",
            user="chillHome",
            password="addinedu1!",
            database="chillHome"
        )


        self.showData() # show the data including origin dataset

        ''' CONNECT '''
        self.btnAdd.clicked.connect(self.addInfo)
        self.btnDelete.clicked.connect(self.deleteInfo)
        self.btnUpdate.clicked.connect(self.updateInfo)

        

    '''------------------------------------------------------------------------------'''
    '''SHOW DATA'''
    def showData(self):
        # Clear existing rows in the table
        self.table.setRowCount(0)

        # Fetch the data from the database
        cursor = self.remote.cursor()
        cursor.execute("SELECT * FROM numberPlates")
        results = cursor.fetchall()

        # update to UI
        for row in results:
            rowIndex = self.table.rowCount()
            self.table.insertRow(rowIndex)

            # Add a checkbox in the first column
            checkbox = QCheckBox()
            checkbox.setChecked(False)  # Default unchecked
            self.table.setCellWidget(rowIndex, 0, checkbox)

            # Insert data into columns
            self.table.setItem(rowIndex, 1, QTableWidgetItem(str(row[1])))  # plateNumber
            self.table.setItem(rowIndex, 2, QTableWidgetItem(str(row[2])))  # createTime
    
    '''------------------------------------------------------------------------------'''
    '''ADD DATA'''
    def addInfo(self):
        # Collect vehicle plate number from the text input
        plateNumber = self.lineNumber.text()
        
        '''need to revise'''
        # If plateNumber already exist -> 'warning' already exist
        #if plateNumber


        # Insert the plate number into the database
        cursor = self.remote.cursor()
        cursor.execute(f"INSERT INTO numberPlates (numberPlate) VALUES ({plateNumber})")

        self.remote.commit()  # Commit the transaction

        # Refresh the table to show the updated data
        self.showData()
    '''------------------------------------------------------------------------------'''
    '''UPDATE DATA'''

    def updateInfo(self):
        cursor = self.remote.cursor()
        rowCount = self.table.rowCount()
        
        for rowIndex in range(rowCount):
            checkbox = self.table.cellWidget(rowIndex, 0)  # Get checkbox 
            if checkbox.isChecked(): #get specific row of clicked check box
                oldPlateNumber = self.table.item(rowIndex, 1).text()
                newPlateNumber, ok = QInputDialog.getText(self, 'Modify Plate Number', 'New Plate Number:')

                if newPlateNumber and ok:
                    cursor.execute("UPDATE numberPlates SET numberPlate = %s WHERE numberPlate = %s", (newPlateNumber, oldPlateNumber))
                    self.remote.commit()
                
        self.showData() 
    '''------------------------------------------------------------------------------'''
    '''DELETE DATA'''
    def deleteInfo(self):
        cursor = self.remote.cursor()
        rowCount = self.table.rowCount()

        for rowIndex in range(rowCount):
            checkbox = self.table.cellWidget(rowIndex, 0)  # Get checkbox 
            plateNumber = self.table.item(rowIndex, 1).text()  # Get the plate number
            if checkbox.isChecked():
                retval = QMessageBox.question(self, 'Delete Info', 'Are you sure to delete?',
                                    QMessageBox.Yes | QMessageBox.No)

                if retval == QMessageBox.Yes:
                    # delete from database
                    cursor.execute("DELETE FROM numberPlates WHERE numberPlate = %s", (plateNumber,))
                    self.remote.commit()
                else:
                    return
        
        self.showData()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindows = WindowClass()
    mywindows.show()

    sys.exit(app.exec_())

    