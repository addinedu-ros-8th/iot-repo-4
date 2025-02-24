import serial
import time

class GasDetectionService:
    def __init__(self):
        self.ser = serial.Serial(port='/dev/cu.usbmodem112301', baudrate=9600, timeout=1)

    def gasDetectionSerial(self):
        try:
            while True:
                if self.ser.in_waiting > 0:
                    gas_data = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    if gas_data.isdigit():
                        gas_level = int(gas_data)
                        print(f"Gas Level: {gas_level}")

                        if gas_level > 700:
                            print("창문이 열립니다 (서보모터 90도)")
                        else:
                            print("창문이 닫힙니다 (서보모터 0도)")

                    time.sleep(0.5)

        except KeyboardInterrupt:
            print("프로그램 종료")
        
        finally:
            self.ser.close()
            print("Serial port closed.")

if __name__ == "__main__":
    sh = GasDetectionService()
    sh.gasDetectionSerial()
