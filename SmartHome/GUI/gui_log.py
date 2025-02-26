# GUI - LOG 화면 구성

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import mysql.connector
from Users import UsersWindow


from_class = uic.loadUiType("Log.ui")[0]

class LogWindow(QMainWindow, from_class) :
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

        
    #Users tab 열기
    def open_usertab(self):
        self.users_window = UsersWindow()
        self.users_window.show()    


    def setup_table(self): 
        cursor = self.remote.cursor()
        query = """
            SELECT 
                IFNULL(u.name, '-') AS userName,
                IFNULL(l.authType, '-') AS authType,
                IFNULL(l.isVerified, '-') AS isVerified,
                IFNULL(l.gasConcentration, '-') AS gasConcentration,
                IFNULL(
                    CASE 
                        WHEN l.gasSafetyLevel = 0 THEN '안전'
                        WHEN l.gasSafetyLevel = 1 THEN '주의'
                        WHEN l.gasSafetyLevel = 2 THEN '위험'
                        ELSE '-'
                    END, 
                '-') AS gasSafetyLevel,
                IFNULL(l.createDate, '-') AS createDate
            FROM smartHomeLog l, users u
            WHERE l.userId = u.uid; 
        """    
        cursor.execute(query)
        data = cursor.fetchall()  # 결과 가져오기
        
        # for row in data:
        self.add_row(data)

        # NULL 값을 '-'로 변환
        # processed_data = [tuple('-' if value is None else value for value in row) for row in data]
        # return processed_data

        # 위의 코드를 풀어쓰면,
        # processed_data = []
        # for row in data:  # data 테이블에서 한 행(row)씩 가져옴
        #     new_row = []  # 변환된 값을 저장할 리스트

        #     for value in row:  # 한 행(row)에서 각 열(column)의 값을 확인
        #         if value is None:
        #             new_row.append('-')  # None이면 '-' 추가
        #         else:
        #             new_row.append(value)  # None이 아니면 원래 값 추가

        #     processed_data.append(tuple(new_row))  # 리스트를 튜플로 변환 후 추가

    def close_connection(self):
        self.cursor.close()
        self.connection.close()

    def add_row(self, logs):
        self.tableWidget.setRowCount(0)

        for log in logs:
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)
            
            # 각 열에 대한 QTableWidgetItem 객체 생성 및 중앙 정렬 설정
            for i in range(6):
                item = QTableWidgetItem(str(log[i]))
                item.setTextAlignment(Qt.AlignCenter)  # 텍스트 중앙 정렬
                self.tableWidget.setItem(row_position, i, item)

    def filter_table(self):
        """선택한 category, status, date 범위에 따라 테이블 필터링"""
        selected_category = self.categoryBox.currentText() # 인증방법 박스
        selected_status = self.statusBox.currentText() # 가스위험여부 박스

        start_date = self.dateStart.currentText()
        end_date = self.dateEnd.currentText()

        if start_date > end_date:  # 날짜 순서 바꾸면 스왑값으로 적용
            start_date, end_date = end_date, start_date

        for row in range(self.tableWidget.rowCount()):
            category_item = self.tableWidget.item(row, 1)  # 인증 방법 (카테고리)
            gas_safety_item = self.tableWidget.item(row, 3)  # 가스 위험 여부
            
            if category_item and gas_safety_item:
                category_text = category_item.text()
                gas_safety_text = gas_safety_item.text()

                # 날짜 비교 (로그가 날짜 컬럼을 가지고 있다고 가정)
                date_item = self.tableWidget.item(row, 5)  # 날짜 컬럼 (있다고 가정)
                
                # 날짜가 NULL인 경우 필터링에서 제외
                if date_item:
                    date_text = date_item.text()
                    
                    if date_text:
                        is_in_date_range = start_date <= date_text <= end_date
                
                    else:
                        is_in_date_range = True  # 날짜 데이터가 없으면 필터링에서 제외

                else:
                    is_in_date_range = True  # 날짜 항목이 아예 없으면 필터링에서 제외

                # 필터 조건 적용 (All이면 해당 필터 무시)
                category_match = (selected_category == "All" or category_text == selected_category)
                status_match = (selected_status == "All" or gas_safety_text == selected_status)

                # 모든 조건을 만족해야 행이 보임
                self.tableWidget.setRowHidden(row, not (category_match and status_match and is_in_date_range))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = LogWindow()
    myWindows.show()

    sys.exit(app.exec_())
