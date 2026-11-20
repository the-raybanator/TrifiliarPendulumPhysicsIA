// NOTE: In this version, I am able to apply and integrate the sensors values with python, to analyze data!
// The ADC now uses the sensor's own 3.3 V supply as its reference (3.3V pin wired to AREF),
// so changes in the Arduino's 5 V rail no longer affect the readings.

#include <Arduino.h>
#include <SoftwareSerial.h>

const float g = 9.81;

/* IMPORTANT: Ensure voltage is float, so that (ref_ADC / max_ADC)
 does NOT result in zero (due to integer division) */
const float voltage_supply = 3.3;   // voltage powering the sensor (3.3V pin)
const float ref_ADC = voltage_supply;   // AREF is wired to the 3.3V pin, so the ADC measures against 3.3 V
const int max_ADC = 1023;

// PINS
const int xPin = A0;

const int BT_TX_PIN = 2;
const int BT_RX_PIN = 3;


// ACCELEROMETER CALIBRATIONS (based on documentation)
// Voltage for every time ACCELERATION INCREASES BY g
const float sensitivity = 0.1 * voltage_supply;


// Biases -> voltage WHEN ACCELERATION = O
// starting value is half of the supply (datasheet: bias is ratiometric)
// can be replaced by values found through using voltage readings, when at rest
const float x_bias_voltage = 1.63;


// CONVERTING THE READINGS
int x_ADC;          // analog pin readings
float x_voltage;    // readings in volts
float x_g;    // acceleration in terms of g

float x_ms2;    // acceleration in m/s2 (final value)

// fix time intervals
const unsigned long INTERVAL_MS = 20;   // 50 samples per second
unsigned long nextSample = 0;

SoftwareSerial bt(BT_TX_PIN, BT_RX_PIN);

void setup() {
  analogReference(EXTERNAL);    // use the voltage on the AREF pin (3.3 V) as the ADC reference
  bt.begin(9600);
}

void loop() {
  if (millis() >= nextSample){
      // converting raw ADC value to ms2
      x_ADC = analogRead(xPin);
      x_voltage = (ref_ADC/max_ADC) * x_ADC;
      x_g = (x_voltage - x_bias_voltage) / sensitivity;
      x_ms2 = x_g * g;

      unsigned long t = millis();
      bt.print(t);
      bt.print(",");
      bt.println(x_ms2);
    }
}
