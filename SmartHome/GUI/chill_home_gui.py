# Main Gui 코드 + LOG 화면

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import urllib.request
from PyQt5.QtGui import *
import mysql.connector

# UI 파일 로드
from_class = uic.loadUiType("chill_home_gui.ui")[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self, userInfo = None):
        super().__init__()
        self.setupUi(self)
        
        #chillguy 이미지
        self.pixmap = QPixmap()
        self.pixmap.load("./data/chillguy.png")

        self.pixmap.scaled(self.label_chillguy.width(), self.label_chillguy.width())
        self.label_chillguy.setPixmap(self.pixmap)
        

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

        self.remote = mysql.connector.connect(
            host="database-1.c7iiuw4kenou.ap-northeast-2.rds.amazonaws.com",
            user="chillHome",
            password="addinedu1!",
            database="chillHome"
        )

        self.btnSearch.clicked.connect(self.userSearch)
        self.editName.returnPressed.connect(self.userSearch)

        ########################### LOG #############################
        # 인덱스(행 번호) 숨기기
        self.tableWidget.verticalHeader().setVisible(False)

        # 행 구분선(그리드) 숨기기
        self.tableWidget.setShowGrid(False)

        # 테이블 초기화
        self.setup_table()

        # 카테고리 콤보박스 & 테이블 연결
        self.categoryBox.currentTextChanged.connect(self.filter_table)

        # status & table 연결
        self.statusBox.currentTextChanged.connect(self.filter_table)

        # 날짜 범위 설정
        today = QDate.currentDate()
        start_date = today.addYears(-1)  # 1년 전
        self.date_range = [start_date.addDays(i) for i in range((today.toJulianDay() - start_date.toJulianDay()) + 1)]
        date_strings = sorted([date.toString("yyyy-MM-dd") for date in self.date_range], reverse=True)

        self.dateStart.addItems(date_strings)
        self.dateEnd.addItems(date_strings)
        self.dateStart.setCurrentIndex(0)  # 기본값: 가장 빠른 날짜
        self.dateEnd.setCurrentIndex(0)  # 기본값: 현재 날짜


        # time & table 연결
        self.dateStart.currentTextChanged.connect(self.filter_table)
        self.dateEnd.currentTextChanged.connect(self.filter_table)
        ########################### LOG #############################

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
            widget = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignCenter)  # 체크박스를 가운데 정렬
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)
            self.tableWidget_2.setCellWidget(row, 0, widget)

            # 사용자 정보 추가
            self.tableWidget_2.setItem(row, 1, QTableWidgetItem(str(result[1])))
            self.tableWidget_2.setItem(row, 2, QTableWidgetItem(str(result[4])))
            self.tableWidget_2.setItem(row, 3, QTableWidgetItem(str(result[5])))
            self.tableWidget_2.setItem(row, 4, QTableWidgetItem(str(result[6])))
            self.tableWidget_2.setItem(row, 5, QTableWidgetItem(str('master' if result[3] else 'normal')))
            self.tableWidget_2.setItem(row, 6, QTableWidgetItem(str(result[6])))
            self.tableWidget_2.setItem(row, 7, QTableWidgetItem(str(result[7])))
    ############### /USER 함수 #############


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())


