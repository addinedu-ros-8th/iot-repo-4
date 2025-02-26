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
from Users import UserWindow
# from userAdd import UserAddWindow
from Users_VehicleInformation import VehicleWindow
from userUpdate import UserUpdateWindow
import requests
from Users import UsersWindow
from gui_log import LogWindow
import serial

# UI 파일 로드
from_class = uic.loadUiType("chill_home_gui.ui")[0]
LogUI = uic.loadUiType("Log.ui")[0]
UsersUI = uic.loadUiType("Users.ui")[0]

URL = "http://192.168.0.52"
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)



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
            time.sleep(0.048)

    def stop(self):
        self.running = False



# 가스 레벨 class
class GasSensorThread(QThread):
    gas_signal = pyqtSignal(int)  # UI로 보낼 시그널

    def __init__(self, port="/dev/ttyACM0", baudrate=9600, parent=None):
        super().__init__()
        self.main = parent
        self.running = True  # 스레드 실행 여부
        
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            self.ser = None

    def run(self):
        while self.running:
            if self.ser and self.ser.in_waiting > 0:
                try:
                    line = self.ser.readline().decode().strip()
                    gas_value = int(line)
                    self.gas_signal.emit(gas_value)  # UI로 전송
                except (ValueError, UnicodeDecodeError):
                    continue  # 잘못된 데이터 무시

    def stop(self):
        self.running = False

        



#메인 CLASS
class WindowClass(QMainWindow, from_class):
    def __init__(self, result):
        super().__init__()
        self.setupUi(self)

        #가스 값 받아와서 적용하면되용
        # gas_value = 0

        # 가스 센서 스레드 실행
        self.gas_thread = GasSensorThread("/dev/ttyACM0")
        self.gas_thread.gas_signal.connect(self.update_gas_level)
        self.gas_thread.start()

        #로그인된 사람 가져오기
        self.result = result
        self.btn_move_to_users.setText(self.result[4])

        #카메라 상태 확인 및 객체 생성
        self.isCameraOn = False
        self.pixmap = QPixmap()
        self.camera = Camera(self)
        self.camera.daemon = True

        #카메라 온오프 버튼
        # self.btn_Camera.clicked.connect(self.clickCamera)
        self.camera.update.connect(self.updateCamera)

        #User Log Tab 이동
        self.btn_move_to_users.clicked.connect(self.open_usertab)
        self.btn_move_to_log.clicked.connect(self.open_logtab)
        
        #chillguy 이미지
        self.pixmap = QPixmap()
        self.pixmap.load("./data/chillguy.png")
        #이미지 크기 조정
        scaled_pixmap = self.pixmap.scaled(self.label_Camera.width(), self.label_Camera.width())
        self.label_Camera.setPixmap(scaled_pixmap)

        # 시간 업데이트 기능 추가
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

        #db 연결
        self.remote = mysql.connector.connect(
            host="database-1.c7iiuw4kenou.ap-northeast-2.rds.amazonaws.com",
            user="chillHome",
            password="addinedu1!",
            database="chillHome"
        )

        self.itemStatuses = self.getItemStatus()

        # 슬라이더 설정
        self.setup_slider(self.slider_led, "led", self.itemStatuses[1])
        self.setup_slider(self.slider_garage, "garage", self.itemStatuses[2])
        self.setup_slider(self.slider_door, "door", self.itemStatuses[3])
        self.setup_slider(self.slider_window, "window", self.itemStatuses[4])
        #카메라 슬라이더
        self.setup_slider(self.slider_camera, "camera", self.itemStatuses[0])


    # 모니터링 상태
    def getItemStatus(self):
        cursor = self.remote.cursor()
        cursor.execute("SELECT * FROM itemStatuses")
        result = cursor.fetchall()
        return result


    # GUI main gas level visualize
    def update_gas_level(self, gas_value):
        """ 가스 수치를 받아서 UI를 업데이트하는 메서드 """

        if gas_value < 500:
            self.label_gas_safe.show()
            self.label_gas_caution.hide()
            self.label_gas_danger.hide()
            gas_safety_level = 0

        elif 500 <= gas_value < 700:
            self.label_gas_safe.hide()
            self.label_gas_caution.show()
            self.label_gas_danger.hide()
            gas_safety_level = 1

        else:  # gas_value >= 700
            self.label_gas_safe.hide()
            self.label_gas_caution.hide()
            self.label_gas_danger.show()
            gas_safety_level = 2

     
        cursor = self.remote.cursor()
        cursor.execute(
            "INSERT INTO smartHomeLog (gasConcentration, gasSafetyLevel) VALUES (%s, %s)",
            (gas_value, gas_safety_level)
        )
        self.remote.commit()


    #Users tab 열기
    def open_usertab(self):
        self.users_window = UsersWindow()
        self.users_window.show()


    #LOG tab 열기
    def open_logtab(self):
        self.log_window = LogWindow()
        self.log_window.show()


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
            # self.btn_Camera.setStyleSheet("background-color: rgb(0, 255, 0);")
            self.isCameraOn = True
            self.cameraStart()

        else:
            # self.btn_Camera.setStyleSheet("background-color: rgb(255, 0, 0);")
            self.isCameraOn = False

            self.cameraStop()

    #카메라 start 함수
    def cameraStart(self):
        self.camera.running = True
        self.camera.start()
        self.video = cv2.VideoCapture(URL + ":81/stream")

    #카메라 stop 함수
    def cameraStop(self):
        self.camera.running = False
        self.video.release() #Test

        #chilly guy 이미지로
        self.pixmap = QPixmap()
        self.pixmap.load("./data/chillguy.png")
        #이미지 크기 조정
        scaled_pixmap = self.pixmap.scaled(self.label_Camera.width(), self.label_Camera.width())
        self.label_Camera.setPixmap(scaled_pixmap)




    #Slider 색상 
    def setup_slider(self, slider, io, status):
        """ 슬라이더 공통 설정 """
        slider.setValue(status[3])
        slider.setStyleSheet(self.get_style(status[3]))  # 초기 스타일 설정
        slider.mousePressEvent = lambda event, s=slider: self.toggle_slider(event, s, io, status)  # 공통 이벤트 핸들러 적용

    def toggle_slider(self, event, slider, io, status):
        """ 슬라이더 클릭 시 ON/OFF 전환 """
        if slider.value() == 0:
            new_value = 1
        else:
            new_value = 0

        slider.setValue(new_value)
        slider.setStyleSheet(self.get_style(new_value))

        super().mousePressEvent(event)

        if io == "camera":
            self.clickCamera()
            return
        
        cursor = self.remote.cursor()
        cursor.execute(f"UPDATE itemStatuses SET itemStatus = {new_value} WHERE itemName = '{io}'")
        self.remote.commit()


        response = requests.post( "http://127.0.0.1:9000/send" , json={"io": io, "value": new_value})
        
        print("Server Response:", response.json())


    # 슬라이더 스타일
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
