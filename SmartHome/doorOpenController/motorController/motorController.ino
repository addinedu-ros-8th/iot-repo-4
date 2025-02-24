#include "ESP32Servo.h"

#define BTN 13
#define SERVOPIN 23

Servo servo;

bool beforeStatus = LOW;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 300;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(BTN, INPUT);
  servo.attach(SERVOPIN);
  servo.write(0);
}

void loop() {
  // put your main code here, to run repeatedly:
  unsigned long currentTime = millis();

  int state = digitalRead(BTN);

  if (state == HIGH && (currentTime - lastDebounceTime) > debounceDelay)
  {
    lastDebounceTime = currentTime;
    Serial.println("test001");

    if (!beforeStatus)
    {
      servo.write(90);
      beforeStatus = true;
      Serial.println("test002");
    } else {
      servo.write(0);
      beforeStatus = false;
      Serial.println("test003");
    }
  }

}
