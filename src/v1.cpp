// NOTE: In this version, I am simply playing around with the sensor, and working on calibration
// The ADC now uses the sensor's own 3.3 V supply as its reference (3.3V pin wired to AREF),
// so changes in the Arduino's 5 V rail no longer affect the readings.

#include <Arduino.h>


const float g = 9.81;

/* IMPORTANT: Ensure voltage is float, so that (ref_ADC / max_ADC)
 does NOT result in zero (due to integer division) */
const float voltage_supply = 3.3;   // voltage powering the sensor (3.3V pin)
const float ref_ADC = voltage_supply;   // AREF is wired to the 3.3V pin, so the ADC measures against 3.3 V
const int max_ADC = 1023;

// PINS
const int xPin = A0;
const int yPin = A1;
const int zPin = A2;


// ACCELEROMETER CALIBRATIONS (based on documentation)
// Voltage for every time ACCELERATION INCREASES BY g
const float sensitivity = 0.1 * voltage_supply;

// Biases -> voltage WHEN ACCELERATION = O
// starting value is half of the supply (datasheet: bias is ratiometric)
// can be replaced by values found through using voltage readings, when at rest
const float x_bias_voltage = 1.63;
const float y_bias_voltage = voltage_supply / 2;
const float z_bias_voltage = voltage_supply / 2;


// CONVERTING THE READINGS
int x_ADC, y_ADC, z_ADC;          // analog pin readings
float x_voltage, y_voltage, z_voltage;    // readings in volts
float x_g, y_g, z_g;    // acceleration in terms of g

float x_ms2, y_ms2, z_ms2;    // acceleration in m/s2 (final value)


void setup() {
  analogReference(EXTERNAL);    // use the voltage on the AREF pin (3.3 V) as the ADC reference
  Serial.begin(9600);
}

void loop() {
  x_ADC = analogRead(xPin);
  y_ADC = analogRead(yPin);
  z_ADC = analogRead(zPin);

  x_voltage = (ref_ADC/max_ADC) * x_ADC;
  y_voltage = (ref_ADC/max_ADC) * y_ADC;
  z_voltage = (ref_ADC/max_ADC) * z_ADC;

  x_g = (x_voltage - x_bias_voltage) / sensitivity;
  y_g = (y_voltage - y_bias_voltage) / sensitivity;
  z_g = (z_voltage - z_bias_voltage) / sensitivity;

  x_ms2 = x_g * g;
  y_ms2 = y_g * g;
  z_ms2 = z_g * g;

  
  Serial.print("VOLTAGES: ");
  Serial.print(x_voltage);
  Serial.print(" ");
  Serial.print(y_voltage);
  Serial.print(" ");
  Serial.print(z_voltage);

  Serial.print(" | INTERMS OF G: ");
  Serial.print(x_g);
  Serial.print(" ");
  Serial.print(y_g);
  Serial.print(" ");
  Serial.print(z_g);

  Serial.print(" | MS2: ");
  Serial.print(x_ms2);
  Serial.print(" ");
  Serial.print(y_ms2);
  Serial.print(" ");
  Serial.println(z_ms2);

  delay(200);
}