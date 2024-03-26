#include <ArduinoJson.h>

#define SENSOR_PIN A0      // Analog pin connected to the moisture sensor
#define LED_green_pin 12   // Green LED connected to pin 12
#define LED_red_pin 13     // Red LED connected to pin 13

unsigned long previousTime = 0;
const long interval = 1000; // Interval to read sensor data (in milliseconds)
const int ARDUINO_ID = 1;   // Change the ID for each Arduino module

StaticJsonDocument<64> doc;  // Adjust the size as per your data

void setup() {
  Serial.begin(9600);
  pinMode(LED_green_pin, OUTPUT);
  pinMode(LED_red_pin, OUTPUT);
}

void loop() {
  unsigned long currentTime = millis();
  if (currentTime - previousTime >= interval) {
    readMoistureSensor();
    sendSensorData();
    previousTime = currentTime;
  }
  
  handleSerialCommands();
}

void readMoistureSensor() {
  int moistureValue = analogRead(SENSOR_PIN);
  doc["arduinoID"] = ARDUINO_ID;
  doc["moisture"] = moistureValue;
}

void sendSensorData() {
  char jsonBuffer[64];
  serializeJson(doc, jsonBuffer);
  Serial.println(jsonBuffer);
}

void handleSerialCommands() {
  if (Serial.available() > 0) {
    String msg = Serial.readStringUntil('\n');
    
    if (msg == "ON") {
      digitalWrite(LED_green_pin, HIGH);
      digitalWrite(LED_red_pin, LOW);
    } else if (msg == "OFF") {
      digitalWrite(LED_green_pin, LOW);
      digitalWrite(LED_red_pin, HIGH);
    } else {
      // Handle invalid command
      digitalWrite(LED_red_pin, HIGH);
      delay(100);
      digitalWrite(LED_red_pin, LOW);
    }
  }