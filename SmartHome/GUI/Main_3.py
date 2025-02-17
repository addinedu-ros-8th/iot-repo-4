# 메인 화면 코드입니다.

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5 import uic

# UI 파일 로드
from_class = uic.loadUiType("Main_3.ui")[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #tab 기능 추가
        #stackedWidget 안에서 버튼 찾기
        # self.btn_main = self.stackedWidget.findChild(QPushButton, "btn_main")
        # self.btn_log = self.stackedWidget.findChild(QPushButton, "btn_log")
        # self.btn_user = self.stackedWidget.findChild(QPushButton, "btn_user")


        self.btn_main.clicked.connect(lambda: self.change_page(0))
        self.btn_main_3.clicked.connect(lambda: self.change_page(0))
        self.btn_main_4.clicked.connect(lambda: self.change_page(0))
        self.btn_log.clicked.connect(lambda: self.change_page(1))
        self.btn_log_3.clicked.connect(lambda: self.change_page(1))
        self.btn_log_4.clicked.connect(lambda: self.change_page(1))
        self.btn_user_3.clicked.connect(lambda: self.change_page(2))
        self.btn_user_4.clicked.connect(lambda: self.change_page(2))


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

    def change_page(self, index):
        # 버튼 클릭 시 QStackedWidget 페이지 변경 """

        if hasattr(self, "stackedWidget"):
            self.stackedWidget.setCurrentIndex(index)
            print("성공")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())


