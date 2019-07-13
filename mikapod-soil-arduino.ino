/*
 Mikapod Soil (Arduino)
 By: Bartlomiej Mika
 Mikaponics
 Date: June 29th, 2019
 License: BSD 3-Clause License

 The source code which powers the Arduino device that collects time-series data
 that will be outputed to the USB serial device.

 The following data will be recorded:
 (1) Humidity/Temperature Sensor --- Si7021
 (2) Barometric Pressure --- MPL3115A2
 (3) Light Sensor --- ALS-PT19
 (4) Soil moisture --- SEN-13637

 This code based on utilizing the following Arduino shields / external sensor(s):
 - SparkFun Weather Shield (DEV-13956)
 - SparkFun Soil Moisture Sensor (SEN-13637)
 
*/

#include <ArduinoJson.h>
#include <Wire.h> //I2C needed for sensors
#include "SparkFunMPL3115A2.h" //Pressure sensor - Search "SparkFun MPL3115" and install from Library Manager
#include "SparkFun_Si7021_Breakout_Library.h" //Humidity sensor - Search "SparkFun Si7021" and install from Library Manager

// Create instance of our sensors.
MPL3115A2 myPressure;
Weather myHumidity;

// Hardware pin definitions
const byte REFERENCE_3V3 = A3;
const byte LIGHT = A1;

// (Soil)
int val = 0; //value for storing moisture value 
int soilPin = A0;//Declare a variable for the soil moisture sensor 
int soilPower = 7;//Variable for Soil moisture Power

// Set variables used by our application
int id_incr_count = 1; // Variable used to keep track of the output count.
char rx_byte = 0;

/**
 * The main entry point into our application.
 */
void setup() {
  // Initialize Serial port
  Serial.begin(9600);
  while (!Serial) continue;

  // SETUP OUR INSTRUMENTS
  //------------------------------------
  // --- Weather Shield ---
  pinMode(REFERENCE_3V3, INPUT);
  pinMode(LIGHT, INPUT);

  //Configure the pressure sensor
  myPressure.begin(); // Get sensor online
  myPressure.setModeBarometer(); // Measure pressure in Pascals from 20 to 110 kPa
  myPressure.setOversampleRate(7); // Set Oversample to the recommended 128
  myPressure.enableEventFlags(); // Enable all three pressure and temp event flags

  //Configure the humidity sensor
  myHumidity.begin();

  // --- Soil Moisture ---
  //Rather than powering the sensor through the 3.3V or 5V pins, 
  //we'll use a digital pin to power the sensor. This will 
  //prevent corrosion of the sensor as it sits in the soil. 
  pinMode(soilPower, OUTPUT);//Set D7 as an OUTPUT
  digitalWrite(soilPower, LOW);//Set to LOW so no power is flowing through the sensor

  // FINISH SETTING UP
  // We must print this JSON string to let our service computer know this
  // code is ready to be polled.
  // Create our JSON object.
  StaticJsonDocument<200> doc;

  // Add system values in the document
  doc["status"] = "READY";
  doc["runtime"] = millis();
  doc["id"] = id_incr_count++;

  // Add an array.
  JsonArray data = doc.createNestedArray("sensors");
  data.add("humidity"); // relative humidity
  data.add("temperature");
  data.add("pressure"); // barometric pressure
  data.add("illuminance");
  data.add("soil");

  // Generate the minified JSON and send it to the Serial port.
  serializeJson(doc, Serial);

  // Start a new line
  Serial.println();
}

/**
 * The main runtime loop of our application.
 */
void loop() {
  if (Serial.available() > 0) {    // is a character available?
    rx_byte = Serial.read();       // get the character

    // check if a number was received
    if ((rx_byte >= '0') && (rx_byte <= '9')) {
      poll_all_instruments();
    }
  }
}


void poll_all_instruments() {
  //Check Humidity Sensor
  float humidity = myHumidity.getRH();

  if (humidity == 998) //Humidty sensor failed to respond
  {
    Serial.println("I2C communication to sensors is not working. Check solder connections.");

    //Try re-initializing the I2C comm and the sensors
    myPressure.begin(); 
    myPressure.setModeBarometer();
    myPressure.setOversampleRate(7);
    myPressure.enableEventFlags();
    myHumidity.begin();
  }
  else
  {
    // Create our JSON object.
    StaticJsonDocument<511> doc;
    
    // Add system values in the document
    doc["status"] = "RUNNING";
    doc["runtime"] = millis();
    doc["id"] = id_incr_count++;

    // HUMIDITY
    JsonObject hum_obj = doc.createNestedObject("humidity");
    hum_obj["value"] = humidity;
    hum_obj["unit"] = "%";
    hum_obj["status"] = 1;
    hum_obj["error"] = "";

    // TEMPERATURE (FROM HUMIDITY INSTRUMENT)
    float temp_h = myHumidity.getTempF();
    JsonObject press_obj = doc.createNestedObject("temperature_primary");
    press_obj["value"] = temp_h;
    press_obj["unit"] = "F";
    press_obj["status"] = 1;
    press_obj["error"] = "";

    // PRESSURE
    float pressure = myPressure.readPressure();
    JsonObject temp_obj = doc.createNestedObject("pressure");
    temp_obj["value"] = pressure;
    temp_obj["unit"] = "Pa";
    temp_obj["status"] = 1;
    temp_obj["error"] = "";

    // TEMPERATURE (FROM PRESSURE INSTRUMENT)
    float temp_p = myPressure.readTempF();
    JsonObject temp2_obj = doc.createNestedObject("temperature_secondary");
    temp2_obj["value"] = temp_p;
    temp2_obj["unit"] = "F";
    temp2_obj["status"] = 1;
    temp2_obj["error"] = "";

    // ALTITUDE
    float altitude = myPressure.readAltitudeFt();
    JsonObject alt_obj = doc.createNestedObject("altitude");
    alt_obj["value"] = altitude;
    alt_obj["unit"] = "ft";
    alt_obj["status"] = 1;
    alt_obj["error"] = "";

    // ILLUMINANCE
    float light_lvl = get_light_level();
    JsonObject light_obj = doc.createNestedObject("illuminance");
    light_obj["value"] = light_lvl;
    light_obj["unit"] = "V";
    light_obj["status"] = 1;
    light_obj["error"] = "";

    // SOIL MOISTURE
    float soil = readSoil();
    JsonObject soil_obj = doc.createNestedObject("soil_moisture");
    soil_obj["value"] = soil;
    soil_obj["unit"] = "SIG";
    soil_obj["status"] = 1;
    soil_obj["error"] = "";
    
    // Generate the minified JSON and send it to the Serial port.
    serializeJson(doc, Serial);

    // Start a new line
    Serial.println();
  }
}

//Returns the voltage of the light sensor based on the 3.3V rail
//This allows us to ignore what VCC might be (an Arduino plugged into USB has VCC of 4.5 to 5.2V)
// https://learn.sparkfun.com/tutorials/arduino-weather-shield-hookup-guide-v12
float get_light_level()
{
  float operatingVoltage = analogRead(REFERENCE_3V3);

  float lightSensor = analogRead(LIGHT);

  operatingVoltage = 3.3 / operatingVoltage; //The reference voltage is 3.3V

  lightSensor = operatingVoltage * lightSensor;

  return (lightSensor);
}


//This is a function used to get the soil moisture content
// Source: https://learn.sparkfun.com/tutorials/soil-moisture-sensor-hookup-guide
int readSoil()
{
    digitalWrite(soilPower, HIGH);//turn D7 "On"
    delay(10);//wait 10 milliseconds 
    val = analogRead(soilPin);//Read the SIG value form sensor 
    digitalWrite(soilPower, LOW);//turn D7 "Off"
    return val;//send current moisture value
}
