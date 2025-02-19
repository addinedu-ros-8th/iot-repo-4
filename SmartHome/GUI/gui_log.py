# GUI - LOG 화면 구성

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import mysql.connector

from_class = uic.loadUiType("gui_log.ui")[0]

class WindowClass(QMainWindow, from_class) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # DB
        self.remote = mysql.connector.connect(
            host = "database-1.c7iiuw4kenou.ap-northeast-2.rds.amazonaws.com",
            port = 3306,
            user = "chillHome",
            password = "addinedu1!",
            database = "chillHome"
        )

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

        
        
    def setup_table(self): 
        cursor = self.remote.cursor()
        query = """
        SELECT 
            io.ioName AS NAME, 
            statusCategory.status AS CATEGORY, 
            logWay.way AS WAY, 
            ioStatus.status AS STATUS, 
            smartHomeLog.logDate AS DATE
        FROM 
            smartHomeLog
        JOIN io ON smartHomeLog.ioId = io.uid
        JOIN ioStatus ON smartHomeLog.statusId = ioStatus.uid
        JOIN logWay ON smartHomeLog.wayId = logWay.uid
        JOIN statusCategory ON ioStatus.status = statusCategory.uid;
        """
        cursor.execute(query)
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


    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()

    sys.exit(app.exec())
