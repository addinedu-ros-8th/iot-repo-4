import serial
import time
import mysql.connector

remote = mysql.connector.connect(
    host = "database-1.c7iiuw4kenou.ap-northeast-2.rds.amazonaws.com",
    user = "chillHome",
    password = "addinedu1!",
    database = "chillHome"
)

cursor = remote.cursor()


class GasDetectionService:
    def __init__(self):
        self.ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)

    def gasDetectionSerial(self):
        try:
            while True:
                if self.ser.in_waiting > 0:
                    gas_data = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    if gas_data.isdigit():
                        gas_level = int(gas_data)
                        print(f"Gas Level: {gas_level}")

                        # gasSafetyLevel 결정
                        if gas_level <= 500:
                            safety_level = 0 # safe
                        elif gas_level <= 699:
                            safety_level = 1 # warning
                        else:
                            safety_level = 2 # Danger

                        # 데이터베이스에 삽입
                        insert_query = "INSERT INTO gasLog (gasConcentration, gasSafetyLevel) VALUES (%s, %s)"
                        cursor.execute(insert_query, (gas_level, safety_level))
                        remote.commit()

                        if gas_level > 700:
                            print("창문이 열립니다 (서보모터 90도)")
                        else:
                            print("창문 닫힌상태 (서보모터 0도)")

        except KeyboardInterrupt:
            print("프로그램 종료")
        
        finally:
            self.ser.close()
            cursor.close()
            remote.close()
            print("Serial port closed.")

if __name__ == "__main__":
    sh = GasDetectionService()
    sh.gasDetectionSerial()
