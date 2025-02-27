import sys
from PyQt5.QtWidgets import *  # PyQt 위젯 포함 (버튼, 라벨, 입력창 등)
from PyQt5.QtGui import *  # PyQt GUI 관련 (아이콘 등, 현재는 사용 안 함)
from PyQt5 import uic  # UI 파일을 로드하기 위한 모듈
from PyQt5.QtCore import *  # QThread 및 시그널을 위한 모듈
import serial  # 시리얼 통신 (RFID 리더기와 연결)
import time  # 딜레이를 위한 time 모듈
import mysql.connector
from faceId import faceIdClass

# UI 파일 로드
from_class = uic.loadUiType("register_rfid.ui")[0]
face_id_ui = uic.loadUiType("faceId.ui")[0]

# RFID 리더기가 연결된 시리얼 포트 설정 (아두이노 포트에 따라 변경 가능)
serial_port = "/dev/ttyACM0"  # 리눅스 환경에서 기본적으로 사용되는 포트
baud_rate = 9600  # 아두이노와 동일한 통신 속도 설정

# 시리얼 포트 연결
ser = serial.Serial(serial_port, baud_rate, timeout=1)

# 시리얼 포트가 열릴 때까지 대기 (2초)
time.sleep(2)

print(f"시리얼 포트 {serial_port} 에 연결되었습니다. RFID 태그를 스캔하세요.")


# RFID 데이터를 읽는 **백그라운드 스레드 (QThread)**
class RFIDReader(QThread):
    # RFID 값을 수신할 때 UI 업데이트를 위한 시그널 생성 (str 값 전달)
    rfid_received = pyqtSignal(str)

    def run(self):
        """RFID 데이터를 계속해서 읽는 무한 루프 (백그라운드 실행)"""
        while True:
            if ser.in_waiting > 0:  # 시리얼 포트에 읽을 데이터가 있는 경우
                data = ser.readline().decode(errors="ignore").strip()  # 데이터를 읽고 문자열로 변환
                print(f"수신된 데이터 : {data}")  # 콘솔에 출력 (디버깅 용도)

                if data.startswith("UID:"):  # UID 데이터인지 확인
                    uid = data.replace("UID:", "").strip()  # "UID:" 부분 제거 후 정리
                    print(f"RFID Tag UID : {uid}")  # 콘솔 출력 (디버깅)
                    self.rfid_received.emit(uid)  # UI에 전달 (시그널 발생)


# RFID GUI 프로그램 (PyQt 윈도우)
class Register_RFID(QMainWindow, from_class):
    def __init__(self, user_data_dic):
        """RFID 등록 프로그램 UI 초기화"""
        super().__init__()
        self.setupUi(self)  # UI 파일 로드
        self.setWindowTitle("Register RFID")  # 창 제목 설정

        self.user_data_dic = user_data_dic

        # RFID 읽기 스레드 실행 (백그라운드에서 실행됨)
        self.rfid_thread = RFIDReader()
        self.rfid_thread.rfid_received.connect(self.update_rfid)  # RFID 값이 수신될 때 UI 업데이트
        self.rfid_thread.start()  # 스레드 실행 (기존 코드에서 빠져 있음)

        # 저장 및 face 등록으로 파일 열기
        self.btn_next.clicked.connect(self.saveUsers)

        #DB 연결
        self.remote = mysql.connector.connect(
            host = "database-1.c7iiuw4kenou.ap-northeast-2.rds.amazonaws.com",
            port = 3306,
            user = "chillHome",
            password = "addinedu1!",
            database = "chillHome"
        )

    #유저 정보 저장
    def saveUsers(self):
        rfid = self.edit_rfid_number.text()
        #중복 확인
        duplicate_sql = f"SELECT COUNT(*) as cnt FROM users WHERE userUid = '{rfid}'"
        cursor = self.remote.cursor()
        cursor.execute(duplicate_sql)
        duplicate_result = cursor.fetchone()
        # print(duplicate_result)
        # print(duplicate_result[0])
        if duplicate_result[0] > 0:
            QMessageBox.warning(self, "경고" ,"이미 등록되어있는 Care입니다. 새로운 카드를 태그해 주십시오")
            return

        #빈칸에러
        if rfid == "":
            QMessageBox.warning(self, "경고" ,"RFID Card가 태그되지 않았습니다 태그해 주십시오")
            return


        sql = "INSERT INTO users (homeId, id, password, name, birthday, phone, userUid, createDate) VALUES (1, %s, SHA2(%s, 256), %s, %s, %s, %s, NOW())"
        cursor = self.remote.cursor()
        cursor.execute(sql, ( 
            self.user_data_dic["id"],
            self.user_data_dic["passwd"],
            self.user_data_dic["name"],
            self.user_data_dic["birthday"],
            self.user_data_dic["phone"],
            rfid
        ))
        self.remote.commit()
        cursor.close()
        self.faceID_window = faceIdClass()
        self.faceID_window.show()
        self.close()      



    # RFID 값 edit에 표시
    def update_rfid(self, uid):
        """RFID 태그 값이 감지되면 UI의 입력 필드 업데이트"""
        self.edit_rfid_number.setText(uid)  # RFID 값 입력창에 표시


# 프로그램 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)  # PyQt 애플리케이션 초기화
    myWindows = Register_RFID()  # RFID 등록 창 생성
    myWindows.show()  # 창 띄우기
    sys.exit(app.exec_())  # 이벤트 루프 실행 (GUI 동작)
