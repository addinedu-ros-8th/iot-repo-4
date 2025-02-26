  /*** 
  Using Step Motor, Push Button, LED, TCRT5000 Sensor
  Controll Garage Door (open, close)
  Detect Obstacle while closing door
  ***/

  #include <Stepper.h>

  const int stepsPerRevolution = 2048;
  const int btn = 2;
  //const int PIR = 3;
  const int PIR_LED = 4;

  Stepper myStepper(stepsPerRevolution,11,9,10,8);
  bool flag = false;
  bool door_open = false;


  void setup(){
    Serial.begin(9600);
    myStepper.setSpeed(10);
    pinMode(btn, INPUT);
    pinMode(A0, INPUT);
  }


  void loop()
  {
    int innerToggle_Status = digitalRead(btn);
    String data = "";

    if ((innerToggle_Status == HIGH && flag == false) || Serial.available() > 0)
    {
      flag = true;

      data = Serial.readStringUntil('\n');
      data.trim();
      Serial.println(data);
      
      if (door_open || data == "GC")
      {
        Serial.println("closing...");
        for (int i = 0; i < stepsPerRevolution; i++)
        {
          myStepper.step(1);  // Move stepper motor one step at a time
          /*-------------------------------------------------------------*/
          /* Check if there is obstacle*/
          int value = analogRead(A0); // TCRT

          if (value > 500)
          { //obstacle detected
            digitalWrite(PIR_LED, HIGH); //LED ON
            Serial.println("Ooops! Obstacle detected! Re-opening door.");
            // Reverse the door movement
            for (int j = 0; j < i; j++)
            {
              myStepper.step(-1);  // Move back the same number of steps taken
            }
            door_open = true;
            return;
          }
          else
          {
            digitalWrite(4, LOW); //obstacle NOT detected
          }
          door_open = false;
        }
      }

      else if(door_open == false || data == "GO")
      {
        Serial.println("opening");
        myStepper.step(-stepsPerRevolution * 2);
        door_open = true;
      }

    }

  else
  {
    flag = false;
  }

  if (Serial.available() > 0) // 데이터 수신 여부 확인
  {
    String command = Serial.readStringUntil('\n'); // 개행 문자까지 읽기
    
    if (command == "OPEN") {
        Serial.println("Gate Opening...");
        gateMotor.write(90); // 문 열기 (각도 조정 가능)
        delay(5000); // 5초 동안 열기 유지
        // gateMotor.write(0); // 다시 닫기
        // Serial.println("Gate Closed.");
    }
  }
}



