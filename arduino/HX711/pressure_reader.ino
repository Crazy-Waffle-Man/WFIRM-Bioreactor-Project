#include "HX711.h"
// #include <MedianFilterLib.h>

#define calibration_factor 8076  // obtained from calibration sketch

// HX711 Load Cell Configuration
#define DOUT A1
#define CLK A0
// #define GAIN 128
// #define PRESSURE_FACTOR 0.0002584  // V/psi, might need to be recalibrated.
// #define EXCITATION_VOLTAGE 5
// #define PSI_TO_MPA 0.00689476  // 1 psi to MPa

HX711 scale;

float last_time = 0;
void setup() {
  Serial.begin(9600);
  scale.begin(DOUT, CLK);
  scale.set_scale(calibration_factor);
  scale.tare();
  last_time = millis();
}

void loop() {
  unsigned long current_time = millis();
  double delta_time = (current_time - last_time) / 1000.0; // in seconds

  float pressure_mbar = scale.get_units();
  // scale.power_down();
  // delay(1000);
  // scale.power_up();
  Serial.println("{\"pressure\": " + String(pressure_mbar) + ", \"delta_time\": " + delta_time + "}"); // receive in raspberry pi. send output value to ESI-MP2. Graph pressure so that we know how to calibrate kp, ki, and kd
}
