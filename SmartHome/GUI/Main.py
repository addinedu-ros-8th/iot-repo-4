import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5 import uic

# UI 파일 로드
from_class = uic.loadUiType("Main.ui")[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 시간 업데이트 기능 추가
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

        # 변경된 QSlider 변수명 반영
        self.slider_led.setStyleSheet(self.get_style(0))
        self.slider_led.mousePressEvent = self.led_slider

        self.slider_garage.setStyleSheet(self.get_style(0))
        self.slider_garage.mousePressEvent = self.garage_slider

        self.slider_door.setStyleSheet(self.get_style(0))
        self.slider_door.mousePressEvent = self.door_slider

        self.slider_window.setStyleSheet(self.get_style(0))
        self.slider_window.mousePressEvent = self.window_slider

    def led_slider(self, event):
        """ 슬라이더 클릭하면 자동으로 ON/OFF 전환 """
        if self.slider_led.value() == 0:
            new_value = 1
        else:
            new_value = 0

        self.slider_led.setValue(new_value)
        self.slider_led.setStyleSheet(self.get_style(new_value))

        super().mousePressEvent(event)

    def garage_slider(self, event):
        """ 슬라이더 클릭하면 자동으로 ON/OFF 전환 """
        if self.slider_garage.value() == 0:
            new_value = 1
        else:
            new_value = 0

        self.slider_garage.setValue(new_value)
        self.slider_garage.setStyleSheet(self.get_style(new_value))

        super().mousePressEvent(event)

    def door_slider(self, event):
        """ 슬라이더 클릭하면 자동으로 ON/OFF 전환 """
        if self.slider_door.value() == 0:
            new_value = 1
        else:
            new_value = 0

        self.slider_door.setValue(new_value)
        self.slider_door.setStyleSheet(self.get_style(new_value))

        super().mousePressEvent(event)

    def window_slider(self, event):
        """ 슬라이더 클릭하면 자동으로 ON/OFF 전환 """
        if self.slider_window.value() == 0:
            new_value = 1
        else:
            new_value = 0

        self.slider_window.setValue(new_value)
        self.slider_window.setStyleSheet(self.get_style(new_value))

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
