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
LogUI = uic.loadUiType("Log.ui")[0]
UsersUI = uic.loadUiType("Users.ui")[0]

#Users class
class UsersWindow(QMainWindow, UsersUI):
    """ usertab 화면 """
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        


#로그화면 class
class LogWindow(QMainWindow, LogUI):
    """ 로그 화면 """
    def __init__(self):
        super().__init__()
        self.setupUi(self)


#카메라 class
class Camera(QThread):
    update = pyqtSignal()

    def __init__(self, sec=0, parent = None):
        super().__init__()
        self.main = parent
        self.running = True

    ######카메라######
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


        #로그 탭으로 이동
        self.btn_move_to_log.clicked.connect(self.open_log_window)
        #Users 탭으로 이동
        self.btn_move_to_users.clicked.connect(self.open_users_window)

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


    #Users tab 열기
    def open_users_window(self):
        self.users_window = UsersWindow()
        self.users_window.show()
        self.close()


    #LOG tab 열기
    def open_log_window(self):
        self.log_window = LogWindow()
        self.log_window.show()
        self.close()


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
            self.label_Camera.setStyleSheet("background-color: black;")

    #카메라 start 함수
    def cameraStart(self):
        self.camera.running = True
        self.camera.start()
        self.video = cv2.VideoCapture(-1)

    #카메라 stop 함수
    def cameraStop(self):
        self.camera.running = False
        self.video.release


    #Slider 색상 
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

        response = requests.post( "http://192.168.0.17:9000/send" , json={"io": io, "value": new_value})
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())
