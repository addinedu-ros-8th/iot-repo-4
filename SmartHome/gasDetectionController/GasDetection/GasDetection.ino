// #include <MQUnifiedsensor.h>
// #include <Servo.h>

// #define placa "Arduino UNO"
// #define Voltage_Resolution 5
// #define gaspin A0  // 가스 센서 아날로그 입력 핀
// #define type "MQ-6"
// #define ADC_Bit_Resolution 10
// #define RatioMQ6CleanAir 10

// MQUnifiedsensor MQ6(placa, Voltage_Resolution, ADC_Bit_Resolution, gaspin, type);
// Servo servo;

// int servoPin = 9;  // 서보모터 PWM 핀
// int buzzerPin = 7;  // 스피커(부저) 핀
// bool window_opened = false;  // 창문 상태 저장

// void setup() 
// {
//   Serial.begin(9600);  // 시리얼 통신 시작

//   servo.write(0);

//   MQ6.setRegressionMethod(1);
//   MQ6.setA(2127.2); MQ6.setB(-2.526);
//   MQ6.init();  

//   servo.attach(servoPin);  // 서보모터 핀 연결
//   pinMode(buzzerPin, OUTPUT);  // 스피커 핀 출력 모드 설정

//   Serial.println("Calibrating...");

//   float calcR0 = 0;

//   for (int i = 1; i <= 10; i++) 
//   {
//     MQ6.update();
//     calcR0 += MQ6.calibrate(RatioMQ6CleanAir);
//     Serial.print(".");
//   }

//   MQ6.setR0(calcR0 / 10);
//   Serial.println(" done!");
// }

// void loop() 
// {
  
//   MQ6.update();
//   float ppm = MQ6.readSensor();  
//   // Serial.println("왜안되냐고 진짜");
//   Serial.println(ppm);  // Python으로 보낼 데이터

//   if (ppm > 100 && !window_opened) 
//   {
//     Serial.println("ALERT");  // Python에서 감지할 문자열
//     servo.write(90);  // 서보모터 90도 회전
//     digitalWrite(buzzerPin, HIGH);  // 스피커 울리기
//     delay(3000);  // 3초 동안 유지
//     // digitalWrite(buzzerPin, LOW);  // 스피커 끄기
//     window_opened = true;  
//   } 
  
//   else if (ppm <= 100 && window_opened) 
//   {
//     Serial.println("SAFE");
//     servo.write(0);  // 서보모터 원래 위치로
//     window_opened = false;
//   }

//   delay(500);  // 센서값 갱신 주기
  
// }




#include <Servo.h>

int gasSensorPin = A0;  
int speakerPin = 9;   // 스피커 핀 정의
Servo myServo;        // 서보 모터 객체 생성
unsigned long alertStartTime = 0;
bool alertActive = false;

void setup() 
{
  Serial.begin(9600);  
  myServo.attach(6);   // 서보 모터 핀 6에 연결 (서보 모터 핀은 실제 연결된 핀으로 변경하세요)
  myServo.write(0);    // 서보 모터를 0도로 설정
  pinMode(speakerPin, OUTPUT); // 스피커 핀을 출력 모드로 설정
  noTone(speakerPin);
}

void loop() 
{
  int gasLevel = analogRead(gasSensorPin);

    if (gasLevel >= 700 && !alertActive) {
        myServo.write(90);
        tone(speakerPin, 1000);
        alertStartTime = millis();  // 현재 시간 저장
        alertActive = true;
    }

    if (alertActive && millis() - alertStartTime >= 3000) {
        noTone(speakerPin);  // 3초 후에 스피커 멈춤
        alertActive = false;
    }

  if (Serial.available() > 0)
  {
    String receivedData = Serial.readStringUntil('\n');
    receivedData.trim();

    if (receivedData == "WO") {
      Serial.println("opened");
      myServo.write(90);
    } else if (receivedData == "WC") {
      Serial.println("closed");
      myServo.write(0);
    } else {
      Serial.println("잘못된 정보입니다.");
    }
  }
}
