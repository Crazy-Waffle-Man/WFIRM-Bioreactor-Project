# Usage
Welcome. This repository was made to hold the source code for a program I participated in at the Wake Forest Institute for Regenerative Medicine.

## Invoking `main.py`

`main.py` requires a few arguments in order to run:
- `--file` or `-r` Points to a file in `./pressure_scripts/` to read.
- `--perfusion-motor-port` or `-f` is the port where the manually controlled motor is found (Via the top part of the GUI created when running `main.py`).
- `--pressure_motor_port` or `-p` is the port where the programattically-controlled motor is connected.
- `--arduino_port` or `-a` is the port where the Arduino is connected. The code for the Arduino assumes use of the HX711 load cell amplifier in conjunction with a pressure sensor.
- `--graph_points` or `-g` is an optional argument that takes an integer and defaults to `50` if none is provided. This controlls how many points can be stored at once by the live graph.
---

## Serial Helpers

All connections to sensors, motors, and the Arduino use a custom AutoSerial API, located in `./serial_helpers.py`. In order to establish a connection (if one exists and the port is not already open), simply call the `AutoSerial` constructor with the port you wish to connect to. This is done in `main.MainWindow#__init__`. The other `serial_helper` is used to send commands to an ESI-MP2 peristaltic pump, and takes an `AutoSerial` object in `ESI_MP2#__init__` in order to establish the connection. `./arduino/HX711/bridge.py` exists as a bridge between an Arduino running `./arduino/HX711/pressure_reader.ino` and the system running the program. It uses `AutoSerial` as well (The Arduino is expected to have been calibrated at this point, make sure you change `CALIBRATION_FACTOR` in the `.ino` files appropriately).

---

## Files
Input files are read by `action_parser.get_action_list`, where the input file must be input as an argument. Input files are expected to adhere to `./pressure_scripts/schema.json`, and VSCode will show tab-completion so long as you start your file like this:
```
{
    "$schema": "./schema.json",
    ...
}
```

Once `main.py` is running, it will save its data to `./logging/` in a custom, human-readable format. Because these files can get very large due to continuous sensor reading, it is not recommended to attempt graphing all of the data at once. 
When running `graph_reconstructor.py`, you will be promted to open a `.log` file from `./logging/`, and if it is larger than `10240B` it will prompt you to choose an interval at which to read data. It is possible to use the generator provided from `graph_reconstructor.read` for more in-depth statistical analysis, but that requires you to write your own python script.

---
## Misc
The backend through which the pressure is maintained is contained within `goal_motor.py`. It allows for far more than what is used in this repository, allowing for custom goal systems if you put in the work. An example of a hard-coded action system can be found [in lines 28-58 of this commit](https://github.com/Crazy-Waffle-Man/WFIRM-Bioreactor-Project/commit/c07190a3e99b623ee2c5d1d71ba563618cd3e792#diff-cebaffaaf8ebb2959179d0e445bc9346f1aae9eac8e5b90af10157bafeeda5a2R28).

All graphing uses `live_graph.LiveGraph`, which is a dressed-up plot from `matplotlib`. Once you set up the object, you can start graphing by calling `LiveGraph#start_animation`, passing a `Generator` to use as the source for data.

---
This repository will not be actively maintained but feel free to open a PR. I'll get around to it eventually.