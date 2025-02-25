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
import requests

# RFID 리더기가 연결된 시리얼 포트 설정 (아두이노 포트에 따라 변경 가능)
serial_port = "/dev/ttyACM0"  # 리눅스 환경에서 기본적으로 사용되는 포트
baud_rate = 9600  # 아두이노와 동일한 통신 속도 설정
ser = serial.Serial(serial_port, baud_rate, timeout=1)

HOST = '192.168.0.11'
PORT = 80

failCount = 0
lockout_time = None  # 인증 차단 시작 시간 (초기값: 없음)
LOCKOUT_DURATION = 3 * 60  # 차단 시간 (초 단위, 3분)


remote = mysql.connector.connect(
    host = "database-1.c7iiuw4kenou.ap-northeast-2.rds.amazonaws.com",
    user = "chillHome",
    password = "addinedu1!",
    database = "chillHome"
)

sql = "SELECT userUid from users"
cursor = remote.cursor()
cursor.execute(sql)
result = cursor.fetchall()

uid_list = []
for row in result:
    uid_list.append(row)

uid_list



def move_servo(position):
    url = f"http://{HOST}:{PORT}/{position}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Servo moved to {90 if position == 'H' else 0} degrees.")
        else:
            print("Failed to control servo:", response.status_code)
    except Exception as e:
        print("Error:", e)


#RFID 태그 감지
def wait_for_rfid():
    print("RFID 태그를 스캔하세요")

    while(True):
        if ser.in_waiting > 0:
            rfid_data = ser.readline().decode(errors="ignore").strip()
            uid = rfid_data.replace("UID:", "").strip()  # "UID:" 부분 제거 후 정리
            return uid

# RFID 인증 함수
def authenticate_rfid(rfid_uid):
    global failCount, lockout_time

    if lockout_time and time.time() - lockout_time < LOCKOUT_DURATION:
        remaining_time = int(LOCKOUT_DURATION - (time.time() - lockout_time))
        print("인증차단")
        return False
    
    sql = "SELECT userUid from users"
    cursor = remote.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()

    uid_list = [(row[0]) for row in result]

    if rfid_uid in uid_list:
        print("인증성공")
        move_servo("DO")
        failCount = 0
        return True
    
    else:
        failCount += 1
        print(f"인증 실패! 누적 실패 횟수: {failCount}")
        move_servo("DC")

        if failCount >= 3:
            lockout_time = time.time()

        return False


move_servo("DO") # 인증 성공시
move_servo("DC") # 인증 실패시 (edited) 

# 메인 실행 루프
if __name__ == "__main__":
    print("RFID 인증 시스템 시작...")
    
    while True:
        uid = wait_for_rfid()  #  RFID 태그 대기
        print(f"감지된 RFID UID: {uid}")

        authenticate_rfid(uid)  #  UID 인증 수행

        time.sleep(1)  #  1초 대기 후 다음 태그 감지

