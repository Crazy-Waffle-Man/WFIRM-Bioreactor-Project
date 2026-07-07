#include "HX711.h"

#define calibration_factor 1  // obtained from calibration sketch

// HX711 Load Cell Configuration
#define DOUT 3
#define CLK 2
#define GAIN 128
#define PRESSURE_FACTOR 0.0002584  // V/psi, might need to be recalibrated.
#define EXCITATION_VOLTAGE 5
#define PSI_TO_MPA 0.00689476  // 1 psi to MPa

HX711 scale;

// PID settings
float setpoint = 1.0; // target pressure in MPa
// to calibrate: ki = kd = 0, then increase kp until it begins oscillating
// slowly increase kd to smooth oscillations
// increase ki to remove consistent error between value and setpoint
float kp = 1.0; // needs calibration
float ki = 1.0; // needs calibration
float kd = 1.0; // needs calibration
unsigned long last_time = 0;
float integral = 0;
float last_error = 0;

void setup() {
  Serial.begin(9600);
  scale.begin(DOUT, CLK);
  scale.set_gain(GAIN);
  scale.set_scale(calibration_factor);
  last_time = millis();
}

void loop() {
  unsigned long current_time = millis();
  double delta_time = (current_time - last_time) / 1000.0; // in seconds

  float raw_reading = scale.get_units(5); // 5 readings
  float voltage = (raw_reading / 1024.0) * EXCITATION_VOLTAGE;
  float pressure_psi = voltage / PRESSURE_FACTOR;
  float pressure_MPa = pressure_psi * PSI_TO_MPA;// well there goes my consistent style

  float pid_output[3];
  pid_compute(delta_time, pressure_MPa, *pid_output)

  Serial.println("{'pressure': " + String(pressure_MPa) + ", 'pid_output': " + String(pid_output[0]) + "}"); // receive in raspberry pi. send output value to ESI-MP2. Graph pressure so that we know how to calibrate kp, ki, and kd
}

void pid_compute(int dt, float value, float output_to) { // best practice would probably be to make setpoint, kp, ki, kd, integral, and last_error parameters here, but I think I'll only need this once.
  float error = setpoint - value;
  float p_out = kp * error;
  integral += error * dt;
  float i_out = ki * integral;
  float derivative = (error - last_error) / dt;
  float d_out = kd * derivative;
  float output = p_out + i_out + d_out;
  last_error = error; // we need this later
  output_to[0] = output;
  output_to[1] = last_error;
  output_to[2] = integral;
}