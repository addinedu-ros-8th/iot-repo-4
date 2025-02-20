import serial
import time

class GasDetectionService:
    def __init__(self):
        self.ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
        self.window_opened = False

    def gasDetectionSerial(self):
        try:
            while True:
                if self.ser.in_waiting > 0:
                    gas_data = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    print(f"Gas Level: {gas_data}")
                    time.sleep(0.05)

                    if int(gas_data) > 700 and not self.window_opened:
                            print("창문이 열립니다")
                            self.window_opened = True
        
        except KeyboardInterrupt:
            print("프로그램 종료")
        
        finally:
            self.ser.close()
            print("Serial port closed.")

if __name__ == "__main__":
    sh = GasDetectionService()
    sh.gasDetectionSerial()