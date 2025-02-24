#include <Stepper.h>

/* Step Motor */
const int stepsPerRevolution = 2048;
Stepper stepperName = Stepper(stepsPerRevolution, 8, 10, 9, 11);

/* Garage Inner Toggle Button */
const int innerToggle = 2;
bool doorOpen = false; // Door state, false = closed, true = open
bool flag = false;


/* PIR Sensor (Obstacle) */
const int PIR = 3;
const int PIR_LED = 4;

/*----------------------------------------------------------------------------------------------------------------*/

void setup() {
  Serial.begin(9600);
  /* Step Motor */
  stepperName.setSpeed(15);

  /* Garage Inner Toggle Button */
  pinMode(innerToggle, INPUT);

  /* PIR sensor, LED */
  pinMode(PIR, INPUT);
  pinMode(PIR_LED, OUTPUT);
}

/*----------------------------------------------------------------------------------------------------------------*/

void loop() {
  /* Garage Inner Toggle Button */
  int innerToggle_Status = digitalRead(innerToggle); 

  if (innerToggle_Status == HIGH && flag == false){
    flag = true;
    if (doorOpen){
      Serial.println("Closing door...");

      for (int i = 0; i < stepsPerRevolution; i++) {
        stepperName.step(1);  // Move stepper motor one step at a time

        /* Check if there is obstacle*/
        int input = digitalRead(PIR);
        digitalWrite(PIR_LED, input); // Turn on debug LED if an obstacle is detected

        if (input == HIGH) {  // Obstacle detected
          Serial.println("Oooops! Obstacle Detected!");
          Serial.println("Reopening the door...");
                
          // Reverse the door movement
          for (int j = 0; j < i; j++) { 
            stepperName.step(-1);  // Move back the same number of steps taken
          }
                
          doorOpen = true;  // Keep door open
          return;  // Exit the function early
        }

        doorOpen = false;
      }
      
    } else {
      Serial.println("Opening door...");
      stepperName.step(-stepsPerRevolution);
      doorOpen = true;
    } 
  }

  if (innerToggle_Status == LOW){
    flag = false;
  }


}
