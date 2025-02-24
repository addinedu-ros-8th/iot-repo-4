# include <Stepper.h>

/* Step Motor */
const int stepsPerRevolution = 2048;
Stepper stepperName = Stepper(stepsPerRevolution, 8, 10, 9, 11);

/* Garage Inner Toggle Button */
const int innerToggle = 2;
bool doorOpen = false; // Door state, false = closed, true = open
bool flag = false;



void setup() {
  Serial.begin(9600);
  /* Step Motor */
  stepperName.setSpeed(15);

  /* Garage Inner Toggle Button */
  pinMode(innerToggle, INPUT);
  

}

void loop() {
  /* Garage Inner Toggle Button */
  int innerToggle_Status = digitalRead(innerToggle); 

  if (innerToggle_Status == HIGH && flag == false){
    flag = true;
    if (doorOpen){
      Serial.println("Closing door...");
      /* Step Motor */
      stepperName.step(stepsPerRevolution);
      doorOpen = false;
    } else {
      Serial.println("Opening door...");
      /* Step Motor */
      stepperName.step(-stepsPerRevolution);
      doorOpen = true;
    } 
  }

  if (innerToggle_Status == LOW){
    flag = false;
  }

}
