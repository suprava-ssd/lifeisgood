#include <SPI.h>
#include <DHT11.h>
#include <SoftwareSerial.h>
#include <LiquidCrystal.h>

// Pin definitions
#define moisture_sensor A0
#define DHT11PIN A1
#define RX 2 // TX of esp8266 is connected with Arduino pin 2
#define TX 3 // RX of esp8266 is connected with Arduino pin 3
#define SS_PIN 10  // Default SS pin for Arduino UNO

// LCD setup
const int rs = 7, en = 6, d4 = 5, d5 = 8, d6 = 9, d7 = 4;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

// DHT11 setup
DHT11 dht11(DHT11PIN);

// WiFi and ThingSpeak setup
int countTrueCommand;
int countTimeCommand;
boolean found = false;
boolean wifiConnected = false;
String WIFI_SSID = "Mad Speed 2.4";     // WIFI NAME
String WIFI_PASS = "#include<iostream>2.4";  // WIFI PASSWORD
String API = "SOTAPNNX6ZWZ9LIA";     // Write API KEY
String HOST = "api.thingspeak.com";
String PORT = "80";
SoftwareSerial esp8266(RX, TX);

// Sensor variables
int moisture_level;
int temperature;
int humidity;
int rain_value = 0;     // From slave
int gas_value = 0;      // From slave
int light_value = 0;    // From slave
bool sendDataSuccessful = false;
unsigned long lastThingSpeakUpdateTime = 0;
const unsigned long thingSpeakUpdateInterval = 20000; // 20 seconds between updates

void setup() {
  Serial.begin(9600);
  esp8266.begin(115200);
  
  // Initialize LCD
  lcd.begin(16, 2);
  lcd.print("Initializing...");
  
  // Initialize SPI as master
  SPI.begin();
  pinMode(SS_PIN, OUTPUT);
  digitalWrite(SS_PIN, HIGH);  // Deselect slave initially
  
  // Connect to WiFi
  lcd.clear();
  lcd.print("Connecting WiFi");
  wifiConnected = connectWiFi();
  
  if (wifiConnected) {
    Serial.println("WiFi connected successfully!");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi Connected!");
    delay(2000);
  } else {
    Serial.println("Failed to connect to WiFi!");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi Connection");
    lcd.setCursor(0, 1);
    lcd.print("Failed!");
    delay(2000);
  }
  
  Serial.println("Master initialized - System ready");
  lcd.clear();
  lcd.print("System ready");
  delay(1000);
}

void loop() {
  // Read local sensors
  int rawMoisture = analogRead(moisture_sensor);
  moisture_level = map(constrain(rawMoisture, 0, 1023), 0, 1023, 100, 0);  // Convert to percentage (inverted)
  
  // Read temperature and humidity from DHT11
  int dht_result = dht11.readTemperatureHumidity(temperature, humidity);
  
  // Get sensor data from slave
  readSlaveData();
  
  // Print sensor values
  Serial.println("\n--- Sensor Readings ---");
  if (dht_result == 0) {  // DHT11 read successful
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.print("°C | Humidity: ");
    Serial.print(humidity);
    Serial.println("%");
  } else {
    Serial.println("DHT11 reading failed");
  }
  
  Serial.print("Soil Moisture: ");
  Serial.print(moisture_level);
  Serial.println("%");
  
  Serial.print("Rain Level: ");
  Serial.print(rain_value);
  Serial.println("%");
  
  Serial.print("Gas Level: ");
  Serial.print(gas_value);
  Serial.println("%");
  
  Serial.print("Light Level: ");
  Serial.print(light_value);
  Serial.println("%");
  
  // Send moisture level to slave
  sendMoistureToSlave();
  
  // Update LCD with sensor data (rotating display)
  updateLCD();
  
  // Send data to ThingSpeak at appropriate intervals
  unsigned long currentMillis = millis();
  if (currentMillis - lastThingSpeakUpdateTime >= thingSpeakUpdateInterval) {
    sendToThingSpeak();
    lastThingSpeakUpdateTime = currentMillis;
  }
  
  delay(5000);  // Main loop delay
}

void readSlaveData() {
  byte receivedData;
  int retries = 0;
  const int maxRetries = 3;
  bool success = false;
  
  while (!success && retries < maxRetries) {
    // Request data from slave
    digitalWrite(SS_PIN, LOW);  // Select slave
    delay(20);  // Give slave time to prepare
    
    // Send command to request data (0xFF)
    SPI.transfer(0xFF);
    delay(20);  // Wait for slave to process
    
    // Read rain value
    receivedData = SPI.transfer(0xFE);  // Send next data request
    byte tempRainValue = receivedData;
    delay(20);
    
    // Read gas value
    receivedData = SPI.transfer(0xFE);  // Send next data request
    byte tempGasValue = receivedData;
    delay(20);
    
    // Read light value
    receivedData = SPI.transfer(0xFE);  // Send next data request
    byte tempLightValue = receivedData;
    
    digitalWrite(SS_PIN, HIGH);  // Deselect slave
    
    // Validate received data
    if (tempRainValue <= 100 && tempGasValue <= 100 && tempLightValue <= 100) {
      rain_value = tempRainValue;
      gas_value = tempGasValue;
      light_value = tempLightValue;
      success = true;
      
      Serial.println("Data received from slave:");
      Serial.println("Rain: " + String(rain_value) + "%, Gas: " + String(gas_value) + "%, Light: " + String(light_value) + "%");
    } else {
      Serial.println("Invalid data received, retry " + String(retries + 1));
      retries++;
      delay(100);  // Wait before retry
    }
  }
  
  if (!success) {
    Serial.println("Failed to get valid data from slave after " + String(maxRetries) + " retries");
    // Keep the last valid values
  }
}

void sendMoistureToSlave() {
  digitalWrite(SS_PIN, LOW);  // Select slave
  delay(20);
  SPI.transfer(moisture_level);  // Send moisture level
  delay(20);
  digitalWrite(SS_PIN, HIGH);  // Deselect slave
  Serial.println("Sent moisture level to slave: " + String(moisture_level) + "%");
}

void updateLCD() {
  // First screen: Moisture and Temperature
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Moist:");
  lcd.print(moisture_level);
  lcd.print("%");
  lcd.setCursor(0, 1);
  lcd.print("Temp:");
  lcd.print(temperature);
  lcd.print((char)223);
  lcd.print("C");
  lcd.setCursor(10, 1);
  lcd.print("H:");
  lcd.print(humidity);
  lcd.print("%");
  delay(3000);
  
  // Second screen: Rain and Gas
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Rain:");
  lcd.print(rain_value);
  lcd.print("%");
  lcd.setCursor(0, 1);
  lcd.print("Gas:");
  lcd.print(gas_value);
  lcd.print("%");
  lcd.setCursor(10, 1);
  lcd.print("L:");
  lcd.print(light_value);
  lcd.print("%");
  delay(3000);
}

void sendToThingSpeak() {
  // Format data string for ThingSpeak with all 6 fields
  String getData = "GET /update?api_key=" + API + 
                  "&field1=" + moisture_level + 
                  "&field2=" + temperature + 
                  "&field3=" + humidity + 
                  "&field4=" + rain_value + 
                  "&field5=" + light_value + 
                  "&field6=" + gas_value;
  
  Serial.println("Sending data to ThingSpeak with all fields:");
  Serial.println("Moisture: " + String(moisture_level) + "%");
  Serial.println("Temperature: " + String(temperature) + "°C");
  Serial.println("Humidity: " + String(humidity) + "%");
  Serial.println("Rain: " + String(rain_value) + "%");
  Serial.println("Light: " + String(light_value) + "%");
  Serial.println("Gas: " + String(gas_value) + "%");
  Serial.println("API string: " + getData);
  
  // Establish TCP connection
  sendCommand("AT+CIPMUX=1", 5, "OK");
  sendCommand("AT+CIPSTART=0,\"TCP\",\"" + HOST + "\"," + PORT, 15, "OK");
  
  // Send data
  sendCommand("AT+CIPSEND=0," + String(getData.length() + 10), 4, ">");
  esp8266.println(getData);
  delay(1500);
  
  // Close connection
  countTrueCommand++;
  sendDataSuccessful = sendCommand("AT+CIPCLOSE=0", 5, "OK");
  
  if (sendDataSuccessful) {
    Serial.println("Data sent successfully to ThingSpeak!");
    Serial.println("***********************");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("ThingSpeak Update");
    lcd.setCursor(0, 1);
    lcd.print("   Successful!   ");
    delay(2000);
  } else {
    Serial.println("Failed to send data. Check connection.");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("ThingSpeak Update");
    lcd.setCursor(0, 1);
    lcd.print("     Failed!     ");
    delay(2000);
    
    // If sending failed, try to reconnect WiFi
    if (!wifiConnected) {
      lcd.clear();
      lcd.print("Reconnecting WiFi");
      wifiConnected = connectWiFi();
    }
  }
}

bool connectWiFi() {
  // Reset the ESP8266 before connecting
  sendCommand("AT+RST", 10, "ready");
  delay(1000);
  
  if (sendCommand("AT", 5, "OK")) {
    Serial.println("ESP8266 responded");
    if (sendCommand("AT+CWMODE=1", 5, "OK")) {
      Serial.println("ESP8266 set to station mode");
      if (sendCommand("AT+CWJAP=\"" + WIFI_SSID + "\",\"" + WIFI_PASS + "\"", 20, "OK")) {
        Serial.println("Connected to WiFi");
        // Get IP address for verification
        sendCommand("AT+CIFSR", 5, "OK");
        return true;
      }
    }
  }
  return false;
}

bool sendCommand(String command, int maxTime, char readReplay[]) {
  countTimeCommand = 0;
  found = false;
  
  Serial.print("Sending command: ");
  Serial.println(command);
  
  while (countTimeCommand < (maxTime * 1)) {
    esp8266.println(command);
    if (esp8266.find(readReplay)) {
      found = true;
      break;
    }
    countTimeCommand++;
    delay(1000);
  }
  
  if (found) {
    Serial.println("Command successful");
    countTrueCommand++;
    countTimeCommand = 0;
    found = false;
    return true; // Command executed successfully
  }
  else {
    Serial.println("Command failed");
    countTrueCommand = 0;
    countTimeCommand = 0;
    found = false;
    return false; // Command execution failed
  }
}