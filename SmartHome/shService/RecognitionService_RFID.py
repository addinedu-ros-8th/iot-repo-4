import cv2
import numpy as np
import dlib
from collections import OrderedDict
import torch 
from torch import nn
from torch.utils.checkpoint import checkpoint
import sys
import mysql.connector
import json
import serial  # 시리얼 통신 (RFID 리더기와 연결)
import time  # 딜레이를 위한 time 모듈
import requests  # HTTP 요청을 위한 requests 모듈

# ==========================
# RFID 리더기 설정
# ==========================

# RFID 리더기가 연결된 시리얼 포트 설정 (운영 환경에 맞게 변경해야 함)
serial_port = "/dev/ttyACM1"  # 리눅스 환경에서 기본적으로 사용되는 시리얼 포트
baud_rate = 9600  # 아두이노와 동일한 통신 속도 (9600 baud)
ser = serial.Serial(serial_port, baud_rate, timeout=1)  # 시리얼 통신 시작

# ==========================
# 서버 및 데이터베이스 설정
# ==========================

# 서보 모터를 제어할 웹 서버의 주소 및 포트 설정
HOST = '192.168.0.11'  # 서보 컨트롤러(아두이노 서버)의 IP 주소
PORT = 80  # 웹 서버의 포트 번호

# 인증 실패 시 차단 설정 변수
failCount = 0  # 연속 인증 실패 횟수
lockout_time = None  # 인증 차단 시작 시간 (초기값: 없음)
LOCKOUT_DURATION = 3 * 60  # 차단 시간 (초 단위, 3분)

# MySQL 데이터베이스 연결 설정 (AWS RDS)
remote = mysql.connector.connect(
    host="database-1.c7iiuw4kenou.ap-northeast-2.rds.amazonaws.com",  # AWS RDS 호스트 주소
    user="chillHome",  # 데이터베이스 사용자 이름
    password="addinedu1!",  # 데이터베이스 비밀번호
    database="chillHome"  # 사용할 데이터베이스 이름
)

# 사용자 UID 목록 가져오기 (사전에 저장된 사용자 리스트)
sql = "SELECT userUid FROM users"
cursor = remote.cursor()  # 데이터베이스 커서 생성
cursor.execute(sql)  # SQL 쿼리 실행
result = cursor.fetchall()  # 결과 가져오기

# ==========================
# 서보 모터 제어 함수
# ==========================

def move_servo(position):
    """
    서보 모터를 이동시키는 함수.
    
    Parameters:
        position (str): "DO" (열기) 또는 "DC" (닫기)
    """
    url = f"http://{HOST}:{PORT}/{position}"  # HTTP 요청을 위한 URL 생성
    try:
        response = requests.get(url)  # HTTP GET 요청 전송
        if response.status_code == 200:
            print(f"Servo moved to {90 if position == 'H' else 0} degrees.")  # 서보 상태 출력
        else:
            print("Failed to control servo:", response.status_code)  # 오류 발생 시 출력
    except Exception as e:
        print("Error:", e)  # 예외 발생 시 출력

# ==========================
# RFID 감지 및 인증
# ==========================

def wait_for_rfid():
    """
    RFID 태그를 스캔할 때까지 대기하는 함수.
    
    Returns:
        str: 감지된 RFID UID 값
    """
    print("RFID 태그를 스캔하세요")  # 사용자 안내 메시지 출력

    while True:
        if ser.in_waiting > 0:  # 시리얼 버퍼에 데이터가 있는 경우
            rfid_data = ser.readline().decode(errors="ignore").strip()  # 데이터를 읽고 디코딩 후 공백 제거
            rfuid = rfid_data.replace("UID:", "").strip()  # "UID:" 부분을 제거하여 순수한 UID 값 추출
            return rfuid  # UID 반환

def authenticate_rfid(rfid_uid):
    """
    RFID UID를 데이터베이스와 비교하여 인증하는 함수.
    
    Parameters:
        rfid_uid (str): 사용자가 태그한 RFID UID 값
    
    Returns:
        bool: 인증 성공 여부 (True: 성공, False: 실패)
    """
    global failCount, lockout_time  # 전역 변수 사용

    # 인증 차단 여부 확인
    if lockout_time and time.time() - lockout_time < LOCKOUT_DURATION:
        remaining_time = int(LOCKOUT_DURATION - (time.time() - lockout_time))  # 남은 차단 시간 계산
        print("인증 차단 상태 (남은 시간:", remaining_time, "초)")
        return False  # 인증 불가

    # 데이터베이스에서 최신 사용자 UID 목록 가져오기
    sql = "SELECT  uid, userUid FROM users"
    cursor = remote.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()

    # 사용자 UID 목록을 리스트 형태로 저장
    rfuid_list = [row[1] for row in result]




    # RFID UID가 데이터베이스에 존재하는지 확인
    if rfid_uid in rfuid_list:
        print("인증 성공! 출입이 허용됩니다.")  # 인증 성공 메시지 출력
        move_servo("DO")  # 서보 모터 문 열기
        failCount = 0  # 실패 횟수 초기화
        cursor = remote.cursor()
        for row in result:
            if row[1] == rfid_uid:
                print(row[0])
                sql_succed = """INSERT INTO smartHomeLog(userid, authType, isVerified, isDoorOpen, createDate)
                                VALUES
                                (%s, %s, %s, %s, Now())
                            """
                data_succed = (row[0], "RFID", "성공", "문열림")
                cursor.execute(sql_succed, data_succed)
                remote.commit()
                cursor.close()   
            

        return True
    else:
        failCount += 1  # 실패 횟수 증가
        print(f"인증 실패! 누적 실패 횟수: {failCount}")  # 실패 메시지 출력
        sql_failed = """INSERT INTO smartHomeLog(authType, isVerified,  createDate)
                                VALUES
                                (%s, %s, Now())
                            """
        data_failed = ("RFID", "실패")
        cursor.execute(sql_failed, data_failed)
        remote.commit()
        cursor.close()  
        # move_servo("DC")  # 서보 모터 문 닫기

        # 3회 이상 연속 실패 시 차단 시간 설정
        if failCount >= 3:
            lockout_time = time.time()
            print("연속 3회 인증 실패! 3분간 인증이 차단됩니다.")

        return False

# ==========================
# 프로그램 실행
# ==========================

if __name__ == "__main__":
    """
    메인 실행 루프.
    RFID 태그를 감지하고 인증을 수행하는 기능을 반복 실행.
    """
    print("RFID 인증 시스템 시작...")

    while True:
        rfuid = wait_for_rfid()  # RFID 태그 감지 대기
        print(f"감지된 RFID UID: {rfuid}")  # 감지된 UID 출력

        authenticate_rfid(rfuid)  # UID 인증 수행

        time.sleep(1)  # 1초 대기 후 다음 태그 감지
