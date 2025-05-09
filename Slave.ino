#include <SPI.h>

// Pin definitions
#define buzzer_red 4
#define buzzer_blue 5
#define buzzer_green 6
#define raindrop_sensor A0
#define mq_sensor A1
#define ldr_sensor A2

// Define data structure for transmission
struct SensorData {
  byte rain;      // 0-100 value indicating rain intensity (0 = no rain, 100 = heavy rain)
  byte gas;       // 0-100 value indicating gas presence (0 = no gas, 100 = high gas)
  byte light;     // 0-100 value indicating light level (0 = bright, 100 = dark)
};

// Variables
volatile byte receivedMoistureLevel = 0;
SensorData slaveData;
volatile boolean dataRequested = false;
byte dataIndex = 0;

void setup() {
  Serial.begin(9600);
  
  // Configure pins
  pinMode(buzzer_red, OUTPUT);
  pinMode(buzzer_blue, OUTPUT);
  pinMode(buzzer_green, OUTPUT);
  pinMode(raindrop_sensor, INPUT);
  pinMode(mq_sensor, INPUT);
  pinMode(ldr_sensor, INPUT);
  
  // Initialize SPI in slave mode
  SPCR |= _BV(SPE);        // Enable SPI in slave mode
  SPI.attachInterrupt();   // Enable SPI interrupt
  
  // Initial buzzer state - all off
  digitalWrite(buzzer_red, LOW);
  digitalWrite(buzzer_blue, LOW);
  digitalWrite(buzzer_green, LOW);
  
  Serial.println("Slave initialized - Ready to receive/transmit data");
}

// SPI interrupt service routine
ISR(SPI_STC_vect) {
  byte receivedValue = SPDR;
  
  // Check if this is a command or data
  // If the received value is 0xFF, it's a request for data
  if (receivedValue == 0xFF) {
    dataRequested = true;
    dataIndex = 0;
    SPDR = slaveData.rain;  // Prepare first byte to send
    return;
  }
  // If the received value is 0xFE, it means we should send the next sensor value
  else if (receivedValue == 0xFE) {
    dataIndex++;
    
    // Send the appropriate sensor value based on dataIndex
    if (dataIndex == 1) {
      SPDR = slaveData.gas;
    } 
    else if (dataIndex == 2) {
      SPDR = slaveData.light;
    }
    else {
      SPDR = 0; // Default response
    }
    return;
  }
  // Otherwise, it's the moisture level from the master
  else {
    receivedMoistureLevel = receivedValue;
    Serial.println("Received moisture from master: " + String(receivedMoistureLevel) + "%");
  }
}

void loop() {
  // Read sensors with multiple samples for stability
  int rainTotal = 0;
  int mqTotal = 0;
  int ldrTotal = 0;
  
  // Take multiple readings and average them for stability
  for (int i = 0; i < 5; i++) {
    rainTotal += analogRead(raindrop_sensor);
    mqTotal += analogRead(mq_sensor);
    ldrTotal += analogRead(ldr_sensor);
    delay(10);
  }
  
  int rainValue = rainTotal / 5;
  int mqValue = mqTotal / 5;
  int ldrValue = ldrTotal / 5;
  
  // Scale sensor values to 0-100 range for transmission
  // For rain sensor: Lower value means more rain
  slaveData.rain = map(1023 - constrain(rainValue, 0, 1023), 0, 1023, 0, 100);
  
  // For gas sensor: Higher value means more gas
  slaveData.gas = map(constrain(mqValue, 0, 1023), 0, 1023, 0, 100);
  
  // For light sensor: Lower value means less light (darker)
  slaveData.light = map(1023 - constrain(ldrValue, 0, 1023), 0, 1023, 0, 100);
  
  // Print sensor values for debugging
  Serial.print("Raindrop raw: ");
  Serial.print(rainValue);
  Serial.print(" (");
  Serial.print(slaveData.rain);
  Serial.print("%) | MQ raw: ");
  Serial.print(mqValue);
  Serial.print(" (");
  Serial.print(slaveData.gas);
  Serial.print("%) | LDR raw: ");
  Serial.print(ldrValue);
  Serial.print(" (");
  Serial.print(slaveData.light);
  Serial.println("%)");
  
  // Determine conditions based on sensor values
  bool isRaining = slaveData.rain > 50;  // Using scaled value for better threshold
  bool gasDetected = slaveData.gas > 30;  // Using scaled value for better threshold
  bool isDark = slaveData.light > 70;     // Using scaled value for better threshold
  
  // Reset all buzzers before setting new states
  digitalWrite(buzzer_red, LOW);
  digitalWrite(buzzer_green, LOW);
  digitalWrite(buzzer_blue, LOW);
  
  // Handle rain detection
  if (isRaining) {
    Serial.println("☔ Rain detected!");
    digitalWrite(buzzer_red, HIGH);
  } else {
    Serial.println("No rain detected");
  }
  
  // Handle gas detection
  if (gasDetected) {
    Serial.println("⚠️ Gas detected! Alert!");
    digitalWrite(buzzer_red, HIGH);  // Red light for gas danger
  } else {
    Serial.println("The ambience is normal outside");
  }
  
  // Handle light detection
  if (isDark) {
    Serial.println("🌙 It's dark outside.");
    digitalWrite(buzzer_green, HIGH);  // Green light for darkness indication
  } else {
    Serial.println("Sunny weather");
  }
  
  // Handle moisture level from master
  if (receivedMoistureLevel <= 30) {
    digitalWrite(buzzer_red, HIGH);  // Red for low moisture (critical)
    Serial.println("🌱 Moisture LOW. Pump ON.");
  } 
  else if (receivedMoistureLevel >= 60) {
    digitalWrite(buzzer_green, HIGH);  // Green for high moisture (good)
    Serial.println("💧 Moisture HIGH. Pump OFF.");
  } 
  else {
    digitalWrite(buzzer_blue, HIGH);  // Blue for medium moisture
    Serial.println("🌾 Moisture MEDIUM. Pump cycling...");
    delay(5000);  // Reduced from 10000 to maintain responsiveness
    digitalWrite(buzzer_blue, LOW);
  }
  
  // Prioritize alerts - gas and rain take precedence over moisture
  if (gasDetected || isRaining) {
    digitalWrite(buzzer_red, HIGH);  // Ensure red light is on for priority alerts
  }
  
  delay(5000);  // Update readings every 5 seconds
}