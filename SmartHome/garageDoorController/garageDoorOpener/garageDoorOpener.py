import serial
import time
import requests
import cv2
import easyocr
import numpy as np
import mysql.connector

# arduino = serial.Serial('/dev/ttyUSB0', 9600)

# ESP32-CAM의 IP 주소
ESP32_CAM_URL = "http://192.168.0.49/capture"

# DB 설정
db = remote = mysql.connector.connect(
    host = "database-1.c7iiuw4kenou.ap-northeast-2.rds.amazonaws.com",
    port = 3306,
    user = "chillHome",
    password = "addinedu1!",
    database = "chillHome"
)

cursor = db.cursor()

# EasyOCR Reader 생성 (한국어, 영어 지원)
reader = easyocr.Reader(['ko', 'en'])

def get_frame():
    """ESP32-CAM에서 이미지를 가져오는 함수"""
    response = requests.get(ESP32_CAM_URL)  # ESP32-CAM에서 캡처한 이미지를 가져옴
    img_array = np.frombuffer(response.content, np.uint8)  # 받은 데이터를 NumPy 배열로 변환
    return cv2.imdecode(img_array, cv2.IMREAD_COLOR)  # 이미지를 OpenCV 형식으로 디코딩하여 반환

def recognize_plate(image):
    """이미지에서 차량 번호판을 인식하는 함수"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 이미지를 그레이스케일로 변환
    result = reader.readtext(gray)  # EasyOCR로 텍스트 인식 시도
    
    for (bbox, text, prob) in result:  # 인식된 텍스트, 바운딩 박스, 신뢰도
        if prob > 0.5:  # 신뢰도가 50% 이상일 경우에만 번호판으로 인정
            return text  # 인식된 번호판 텍스트 반환
    return None  # 번호판을 인식하지 못하면 None 반환

while True:
    frame = get_frame()  # ESP32-CAM에서 프레임을 가져옴
    plate_number = recognize_plate(frame)  # 번호판 인식 함수 호출
    
    if plate_number:  # 번호판을 인식했다면
        print(f"인식된 번호판: {plate_number}")
        
        # MySQL 데이터베이스에서 번호판 확인
        cursor.execute("SELECT * FROM numberPlates WHERE numberPlate = %s", (plate_number,))
        result = cursor.fetchone()  # 번호판에 대한 결과를 가져옴
        
        if result:  # DB에 번호판이 등록되어 있다면
            print("등록된 차량입니다. 문을 엽니다.")
            time.sleep(5)  # 모터가 작동하고 나서 5초 대기 (문 열림 유지)
        else:
            print("등록되지 않은 차량입니다.")
    
    time.sleep(2)  # 2초마다 한 번씩 이미지를 가져와서 번호판 인식
