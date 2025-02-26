#include <Servo.h>

int gasSensorPin = A0;  
int speakerPin = 9;   // 스피커 핀 정의
Servo myServo;        // 서보 모터 객체 생성
unsigned long alertStartTime = 0;
bool alertActive = false;
unsigned long lastPrintTime = 0;  // 마지막으로 출력한 시간 기록

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
  unsigned long currentMillis = millis();  // 현재 시간 저장

  // 0~500: 10초(10000ms)마다 한 번 출력 -> 가장 최근값 출력
  
  if (gasLevel <= 500) {
    if (currentMillis - lastPrintTime >= 10000) {  // 10초 경과 체크
        Serial.println(gasLevel);
        lastPrintTime = currentMillis;  // 마지막 출력 시간 업데이트
    }
  } 
  
  // 501 이상: 즉시 출력
  else {
    if (currentMillis - lastPrintTime >= 100) {   // 0.1초 간격으로 표시
      Serial.println(gasLevel);
      lastPrintTime = currentMillis;  // 마지막 출력 시간 업데이트
    }
  }  


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
