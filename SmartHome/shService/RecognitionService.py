import serial
import time

class RecognitionService:
    def __init__(self):
        self.ser = serial.Serial("/dev/cu.usbmodem1401", 9600)

    def doorOpenSerial(self):
        while True:
            auth = input("얼굴인증 또는 RFID 결과를 입력해주세요")
            self.ser.write(auth.encode("UTF-8"))
            time.sleep(1)
            line = self.ser.readline().decode('utf-8').strip()
            print(f"[Arduino] {line}")
            time.sleep(1)
            
                


if __name__ == "__main__":
    sh = RecognitionService()
    sh.doorOpenSerial()