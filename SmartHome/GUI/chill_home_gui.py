# Main Gui 코드 + LOG 화면

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import urllib.request
from PyQt5.QtGui import *
import mysql.connector
import time
import cv2
from userAdd import UserWindow
from Users_VehicleInformation import VehicleWindow
from userUpdate import UserUpdateWindow
import requests

# UI 파일 로드
from_class = uic.loadUiType("chill_home_gui.ui")[0]
userAddUi = uic.loadUiType("userAdd.ui")[0]
vehicleUi = uic.loadUiType("Users_VehicleInformation.ui")[0]


class Camera(QThread):
    update = pyqtSignal()

    def __init__(self, sec=0, parent = None):
        super().__init__()
        self.main = parent
        self.running = True

    def run(self):
        while self.running == True:
            self.update.emit()
            time.sleep(0.04)

    def stop(self):
        self.running = False

class WindowClass(QMainWindow, from_class):
    def __init__(self, userInfo = None):
        super().__init__()
        self.setupUi(self)


        #카메라 상태 확인 및 객체 생성
        self.isCameraOn = False
        self.pixmap = QPixmap()
        self.camera = Camera(self)
        self.camera.daemon = True

        #카메라 온오프 버튼
        self.btn_Camera.setStyleSheet("background-color: rgb(255, 0, 0);")
        self.btn_Camera.clicked.connect(self.clickCamera)
        self.camera.update.connect(self.updateCamera)
        
        #chillguy 이미지
        self.pixmap = QPixmap()
        self.pixmap.load("./data/chillguy.png")

        scaled_pixmap = self.pixmap.scaled(self.label_chillguy.width(), self.label_chillguy.width())
        self.label_chillguy.setPixmap(scaled_pixmap)

        #chiily guy 투명도 적용
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.3)
        self.label_chillguy.setGraphicsEffect(opacity_effect)

        #초기화면설정
        self.change_page(0)

        #tabmeunu 버튼 
        self.btn_main.clicked.connect(lambda: self.change_page(0))
        self.btn_main_2.clicked.connect(lambda: self.change_page(0))
        self.btn_main_3.clicked.connect(lambda: self.change_page(0))
        self.btn_log.clicked.connect(lambda: self.change_page(1))
        self.btn_log_2.clicked.connect(lambda: self.change_page(1))
        self.btn_log_3.clicked.connect(lambda: self.change_page(1))
        self.btn_user_2.clicked.connect(lambda: self.change_page(2))
        self.btn_user_3.clicked.connect(lambda: self.change_page(2))

        self.btnAdd.clicked.connect(self.userAdd)
        self.btnVehicle.clicked.connect(self.vehicleInfo)
        self.btnUpdate.clicked.connect(self.userUpdate)
        self.btnDelete.clicked.connect(self.userDelete)


        # 시간 업데이트 기능 추가
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

        # 슬라이더 설정
        self.setup_slider(self.slider_led, "led")
        self.setup_slider(self.slider_garage, "garage")
        self.setup_slider(self.slider_door, "door")
        self.setup_slider(self.slider_window, "window")

        self.remote = mysql.connector.connect(
            host="database-1.c7iiuw4kenou.ap-northeast-2.rds.amazonaws.com",
            user="chillHome",
            password="addinedu1!",
            database="chillHome"
        )

        self.btnSearch.clicked.connect(self.userSearch)
        self.editName.returnPressed.connect(self.userSearch)

    # 카메라 On    
    def updateCamera(self):
        retval, image = self.video.read()

        if retval:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            h, w, c = image.shape
            qimage = QImage(image.data, w, h, w*c, QImage.Format_RGB888)

            self.pixmap = self.pixmap.fromImage(qimage)
            self.pixmap = self.pixmap.scaled(self.label_Camera.width(), self.label_Camera.height())

            self.label_Camera.setPixmap(self.pixmap)

    #카메라 클릭 했을 때 함수
    def clickCamera(self):
        if self.isCameraOn == False:
            self.btn_Camera.setStyleSheet("background-color: rgb(0, 255, 0);")
            self.isCameraOn = True

            self.cameraStart()

        else:
            self.btn_Camera.setStyleSheet("background-color: rgb(255, 0, 0);")
            self.isCameraOn = False

            self.cameraStop()

    #카메라 start 함수
    def cameraStart(self):
        self.camera.running = True
        self.camera.start()
        self.video = cv2.VideoCapture(-1)

    #카메라 stop 함수
    def cameraStop(self):
        self.camera.running = False
        self.video.release


    # 버튼 눌러서 tab 변경 
    def change_page(self, index):
        # 버튼 클릭 시 QStackedWidget 페이지 변경 """

        if hasattr(self, "stackedWidget"):
            self.stackedWidget.setCurrentIndex(index)
            if hasattr(self, "label_title"):
                if index == 0:
                    self.label_title.setText("Main")
                    self.btn_main.setStyleSheet("background-color: rgb(204, 221, 255);")
                elif index == 1:
                    self.label_title.setText("LOG")
                    self.btn_log_2.setStyleSheet("background-color: rgb(204, 221, 255);")
                elif index == 2:
                    self.label_title.setText("USER")
                    self.btn_user_3.setStyleSheet("background-color: rgb(204, 221, 255);")
                else:
                    print("label title failed")

        else:
            print("실패")


    def setup_slider(self, slider, io):
        """ 슬라이더 공통 설정 """
        slider.setStyleSheet(self.get_style(0))  # 초기 스타일 설정
        slider.mousePressEvent = lambda event, s=slider: self.toggle_slider(event, s, io)  # 공통 이벤트 핸들러 적용

    def toggle_slider(self, event, slider, io):
        """ 슬라이더 클릭 시 ON/OFF 전환 """
        if slider.value() == 0:
            new_value = 1
        else:
            new_value = 0

        slider.setValue(new_value)
        slider.setStyleSheet(self.get_style(new_value))

        super().mousePressEvent(event)

        response = requests.post( "http://127.0.0.1:9000/send" , json={"io": io, "value": new_value})
        print("Server Response:", response.json())



    def get_style(self, value):
        """ ON/OFF 상태에 따라 스타일 변경 """
        if value == 1:
            background_color = "#4CAF50"  # 초록색 (ON)
            handle_position = "left: 40px;"  # 핸들 오른쪽
        else:
            background_color = "#FF3B30"  # 빨간색 (OFF)
            handle_position = "left: 2px;"  # 핸들 왼쪽

        return f"""
            QSlider::groove:horizontal {{
                background: {background_color};
                height: 20px;
                border-radius: 10px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                border: 1px solid #aaa;
                width: 24px;
                height: 24px;
                border-radius: 12px;
                margin: -2px 0;
                {handle_position}
            }}
        """

    def update_time(self):
        """ 현재 날짜를 QLabel에 표시 """
        current_date = QDateTime.currentDateTime().toString("yyyy - MM - dd dddd")
        self.label_date.setText(current_date)

    ###############LOG 함수#################

    def setup_table(self): 
        cursor = self.remote.cursor()
        cursor.execute("SELECT * FROM smartHomeLog;")
        data = cursor.fetchall()  # 결과 가져오기
        
        for row in data:
            self.add_row(row)


    def close_connection(self):
        self.cursor.close()
        self.connection.close()

    def add_row(self, data):
        row_position = self.tableWidget.rowCount()  # 현재 행 개수 확인
        self.tableWidget.insertRow(row_position)  # 새 행 추가

        for col, value in enumerate(data):
            item = QTableWidgetItem(value)  # 아이템 생성
            item.setTextAlignment(Qt.AlignCenter)  # 가운데 정렬 적용
            self.tableWidget.setItem(row_position, col, item)  # 테이블에 추가

    def filter_table(self):
        """선택한 category, status, date 범위에 따라 테이블 필터링"""
        selected_category = self.categoryBox.currentText()
        selected_status = self.statusBox.currentText()
        start_date = self.dateStart.currentText()
        end_date = self.dateEnd.currentText()

        if start_date > end_date: # 날짜 순서 바꾸면 스왑값으로 적용
            start_date, end_date = end_date, start_date

        for row in range(self.tableWidget.rowCount()):
            category_item = self.tableWidget.item(row, 1)  # category 열
            status_item = self.tableWidget.item(row, 3)  # status 열
            date_item = self.tableWidget.item(row, 4)  # date 열

            if category_item and status_item and date_item:
                category_text = category_item.text()
                status_text = status_item.text()
                date_text = date_item.text()

                # 날짜 비교
                if start_date == end_date:
                    is_in_date_range = (date_text == start_date)  # 특정 날짜만 선택
                
                else:
                    is_in_date_range = start_date <= date_text <= end_date  # 범위 선택

                # 필터 조건 적용 (All이면 해당 필터 무시)
                category_match = (selected_category == "All" or category_text == selected_category)
                status_match = (selected_status == "All" or status_text == selected_status)

                # 모든 조건을 만족해야 행이 보임
                self.tableWidget.setRowHidden(row, not (category_match and status_match and is_in_date_range))
    
    ###############LOG 함수#################


    ############### USER 함수 ##############
    def userSearch(self):
        self.tableWidget_2.setRowCount(0)

        params = ""

        name = self.editName.text()

        if name != "":
            params = "WHERE name = '" + name + "'"

        cursor = self.remote.cursor()
        cursor.execute(f"SELECT * FROM users {params}")
        results = cursor.fetchall()
        
        for result in results:
            row = self.tableWidget_2.rowCount()
            self.tableWidget_2.insertRow(row)

            checkbox = QCheckBox()
            checkbox.setChecked(False)
            self.tableWidget_2.setCellWidget(row, 0, checkbox)

            # 사용자 정보 추가
            self.tableWidget_2.setItem(row, 1, QTableWidgetItem(str(result[1])))
            self.tableWidget_2.setItem(row, 2, QTableWidgetItem(str(result[4])))
            self.tableWidget_2.setItem(row, 3, QTableWidgetItem(str(result[5])))
            self.tableWidget_2.setItem(row, 4, QTableWidgetItem(str(result[6])))
            self.tableWidget_2.setItem(row, 5, QTableWidgetItem(str('master' if result[3] else 'normal')))
            self.tableWidget_2.setItem(row, 6, QTableWidgetItem(str(result[6])))
            self.tableWidget_2.setItem(row, 6, QTableWidgetItem(str(result[7])))
            self.tableWidget_2.setItem(row, 7, QTableWidgetItem(str(result[8])))
    ############### /USER 함수 #############

    def vehicleInfo(self):
        self.main_window = VehicleWindow()
        self.main_window.show()


    def userAdd(self):
        self.main_window = UserWindow()
        self.main_window.show()

    def userUpdate(self):
        ids = list()

        cursor = self.remote.cursor()
        rowCount = self.tableWidget_2.rowCount()

        for rowIndex in range(rowCount):
            checkbox = self.tableWidget_2.cellWidget(rowIndex, 0)
            id = self.tableWidget_2.item(rowIndex, 1).text()
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
        rowCount = self.tableWidget_2.rowCount()

        for rowIndex in range(rowCount):
            checkbox = self.tableWidget_2.cellWidget(rowIndex, 0)
            id = self.tableWidget_2.item(rowIndex, 1).text()
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
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())

