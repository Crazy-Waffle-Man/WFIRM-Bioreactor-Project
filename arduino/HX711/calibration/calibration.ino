#include <HX711.h>

const int DOUT = A1;
const int CLK = A0;

HX711 scale;
float calibration_factor = 8010;

long zero_factor = 1;

void setup() {
  Serial.begin(9600);
  Serial.println("HX711 calibration sketch\nRemove all weight from scale\nAfter readings begin, place known weight on scale\n +/- to increase/decrease calibration factor");
  scale.begin(DOUT, CLK);
  scale.set_scale(calibration_factor);
  scale.tare();
  zero_factor = scale.read_average();
  Serial.print("Zero factor: ");
  Serial.println(zero_factor);
}

void loop() {
  // put your main code here, to run repeatedly:
  // scale.set_scale(calibration_factor);
  Serial.print("Average of last 25 readings: ");
  double reading = scale.get_units(25);
  Serial.print(reading);
  Serial.print(" mbar, calibration_factor: ");
  Serial.println(calibration_factor);
  if (Serial.available()) {
    char input = Serial.read();
    if (input == '+') {
      calibration_factor += 10;
    } else if (input == '-') {
      calibration_factor -= 10;
    }
  }
}
