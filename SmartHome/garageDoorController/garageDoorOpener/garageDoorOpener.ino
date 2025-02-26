/*** 
Using Step Motor, Push Button, LED, TCRT5000 Sensor
Controll Garage Door (open, close)
Detect Obstacle while closing door
***/

#include <Stepper.h>

const int stepsPerRevolution = 2048;
const int btn = 2;
const int PIR = 3;
const int PIR_LED = 4;

Stepper myStepper(stepsPerRevolution,11,9,10,8);
bool flag = false;
bool door_open = false;


void setup(){
  Serial.begin(9600);
  myStepper.setSpeed(10);
  pinMode(btn, INPUT);
}


void loop()
{
  // ESP32-CAM이 "OPEN" 메시지를 보내면 문 열기
  if (Serial.available() > 0) 
  {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "OPEN") 
    {
      Serial.println("등록된 차량입니다. 문을 엽니다.");
      myStepper.step(-stepsPerRevolution * 2);  
      door_open = true;
    } 
  }

  int innerToggle_Status = digitalRead(btn);

  if (innerToggle_Status == HIGH && flag == false)
  {
    flag = true;


    if (door_open)
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

    else
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
}



