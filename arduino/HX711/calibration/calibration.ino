#include "HX711.h"

#define DOUT 3
#define CLK 2

HX711 scale
float calibration_factor = 1

void setup() {
  Serial.begin(9600);
  Serial.println("HX711 calibration sketch\nRemove all weight from scale\nAfter readings begin, place known weight on scale\n +/- to increase/decrease calibration factor");
  scale.begin(DOUT, CLK);
  scale.set_scale();
  scale.tare();
  long zero_factor = scale.read_average();
  Serial.print(Zero factor: );
  Serial.println(zero_factor);
}

void loop() {
  // put your main code here, to run repeatedly:
  scale.set_scale(calibration_factor);

  Serial.print("Reading: ");
  Serial.print(scale.get_units(), 1);
  Serial.print(" MPa, calibration_factor: ");
  Serial.println(calibration_factor);
  if (Serial.available()) {
    char input = Serial.read();
    if (input == '+') {
      calibration_factor += 10;
    } else if (input == '-') {
      calibration_factor -= 10
    }
  }
}
