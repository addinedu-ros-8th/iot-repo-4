import serial
import time

class GasDetectionService:
    def __init__(self):
        self.ser = serial.Serial("/dev/cu.usbmodem1401", 9600)

    def gasDetectionSerial(self):
        while True:
            gas = input("가스 정보를 입력해주세요")
            self.ser.write(gas.encode("utf-8"))
            time.sleep(1)


if __name__ == "__main__":
    sh = GasDetectionService()
    sh.gasDetectionSerial()