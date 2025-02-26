#include <WiFi.h>
#include <ESP32Servo.h>

#define BTN 13
#define SERVOPIN 23
#define LEDBTN 15
#define LEDPIN 2

const char *ssid = "AIE_509_2.4G";
const char *password = "addinedu_class1";

NetworkServer server(80);

Servo servo;

bool buttonStatus = LOW;
bool ledStatus = LOW;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 300;

void setup() {
  Serial.begin(115200);
  pinMode(BTN, INPUT);
  pinMode(LEDBTN, INPUT);
  pinMode(LEDPIN, OUTPUT);
  servo.attach(SERVOPIN);
  servo.write(0);

  delay(10);

  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  server.begin();
}

void loop() {
  NetworkClient client = server.accept();  

  if (client) {                    
    Serial.println("New Client."); 
    String currentLine = "";        
    while (client.connected()) {    
      if (client.available()) {     
        char c = client.read();     
        Serial.write(c);            
        if (c == '\n') {            
          if (currentLine.length() == 0) {
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println();

            client.print("Click <a href=\"/H\">here</a> to turn the LED on pin 5 on.<br>");
            client.print("Click <a href=\"/L\">here</a> to turn the LED on pin 5 off.<br>");

            client.println();
            break;
          } else {
            currentLine = "";
          }
        } else if (c != '\r') {
          currentLine += c;
        }

        if (currentLine.endsWith("GET /DO")) {
          servo.write(90);
          buttonStatus = true;
        }
        if (currentLine.endsWith("GET /DC")) {
          servo.write(0);
          buttonStatus = false;
        }

        if (currentLine.endsWith("GET /LO")) {
          digitalWrite(LEDPIN, HIGH);
          ledStatus = true;
        }
        if (currentLine.endsWith("GET /LF")) {
          digitalWrite(LEDPIN, LOW);
          ledStatus = false;
        }
      }
    }
    // close the connection:
    client.stop();
    Serial.println("Client Disconnected.");
  }

  unsigned long currentTime = millis();

  int state = digitalRead(BTN);

  if (state == HIGH && (currentTime - lastDebounceTime) > debounceDelay)
  {
    lastDebounceTime = currentTime;

    if (!buttonStatus)
    {
      servo.write(90);
      buttonStatus = true;
    } else {
      servo.write(0);
      buttonStatus = false;
    }
  }

  int ledState = digitalRead(LEDBTN);

  if (ledState == HIGH && (currentTime - lastDebounceTime) > debounceDelay)
  {
    lastDebounceTime = currentTime;

    if (!ledStatus)
    {
      digitalWrite(LEDPIN, HIGH);
      ledStatus = true;
    } else {
      digitalWrite(LEDPIN, LOW);
      ledStatus = false;
    }
  }
}