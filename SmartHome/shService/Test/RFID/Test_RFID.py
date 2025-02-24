import serial
import time

# RFID 리더기가 연결된 시리얼 포트 설정 (아두이노에 따라 변경 가능)
serial_port = "/dev/ttyACM0"  
baud_rate = 9600  # 아두이노에서 설정한 통신 속도와 동일해야 함

# 시리얼 포트 연결
ser = serial.Serial(serial_port, baud_rate, timeout=1)

# 시리얼 포트가 열릴 때까지 대기
time.sleep(2)

print(f"시리얼 포트 {serial_port} 에 연결되었습니다. RFID 태그를 스캔하세요.")

def read_rfid():
    while True:
        # 시리얼 버퍼에 수신된 데이터가 있는지 확인
        if ser.in_waiting > 0:
            # 데이터를 읽고 UTF-8로 디코딩 (깨진 문자 무시)
            data = ser.readline().decode(errors='ignore').strip()
            
            # 원본 데이터를 출력하여 디버깅
            print(f"수신된 데이터: {data}")

            # "UID:" 로 시작하는 경우, RFID 태그 데이터로 인식
            if data.startswith("UID:"):
                # "UID:" 문자열을 제거하여 순수한 UID 값만 저장
                uid = data.replace("UID:", "").strip()
                print(f"RFID Tag UID: {uid}")

# RFID 읽기 시작
read_rfid()
