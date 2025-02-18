# Main Gui 코드 + LOG 화면

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import urllib.request
from PyQt5.QtGui import *

# UI 파일 로드
from_class = uic.loadUiType("chill_home_gui.ui")[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self, userInfo = None):
        super().__init__()
        self.setupUi(self)
        
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


        # 시간 업데이트 기능 추가
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

        # 슬라이더 설정
        self.setup_slider(self.slider_led)
        self.setup_slider(self.slider_garage)
        self.setup_slider(self.slider_door)
        self.setup_slider(self.slider_window)

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


    def setup_slider(self, slider):
        """ 슬라이더 공통 설정 """
        slider.setStyleSheet(self.get_style(0))  # 초기 스타일 설정
        slider.mousePressEvent = lambda event, s=slider: self.toggle_slider(event, s)  # 공통 이벤트 핸들러 적용

    def toggle_slider(self, event, slider):
        """ 슬라이더 클릭 시 ON/OFF 전환 """
        if slider.value() == 0:
            new_value = 1
        else:
            new_value = 0

        slider.setValue(new_value)
        slider.setStyleSheet(self.get_style(new_value))

        super().mousePressEvent(event)

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

    def setup_table(self): # 임시로 데이터 넣어놓을게요 DB랑 연결해야함
        data = [
            ["재니", "Door Lock", "Face ID", "OPEN", "2025-02-13"],
            ["-", "LED", "Switch", "OFF", "2025-02-13"],
            ["-", "Window", "GUI", "OPEN", "2025-02-13"],
            ["-", "Garage", "GUI", "CLOSE", "2025-02-13"],
            ["재니", "Door Lock", "Smart Key", "OPEN", "2025-02-12"],
        ]

        self.tableWidget.setRowCount(0)  # 기존 행 삭제
        
        for row in data:
            self.add_row(row)

    def add_row(self, data):
        row_position = self.tableWidget.rowCount()  # 현재 행 개수 확인
        self.tableWidget.insertRow(row_position)  # 새 행 추가

        for col, value in enumerate(data):
            item = QTableWidgetItem(value)  # 아이템 생성
            item.setTextAlignment(Qt.AlignCenter)  # 가운데 정렬 적용
            self.tableWidget.setItem(row_position, col, item)  # 테이블에 추가
    
    ###############LOG 함수#################


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())


