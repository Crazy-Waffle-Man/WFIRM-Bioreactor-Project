import json
from typing import Callable
from serial_helpers import ESI_MP2
from goal_motor import *
from arduino.HX711.bridge import get_data_from_arduino

graph: LiveGraph
motor: GoalMotor
action_list = ActionList([])

direction: int = 0
def adaptive_motor_speed(target: int | float, motor: ESI_MP2, value: int | float | Callable, tolerance: int | float):
    global direction
    if isinstance(value, Callable):
        value = value()
    if value is None:
        # print("value is none")
        return
    assert isinstance(value, (float, int))
    if value < target - tolerance:
        # print("Value less than goal")
        if direction != 1:
            motor.turn_cw()
            direction = 1
    elif value > target + tolerance:
        # print("Value greater than goal")
        if direction != -1:
            motor.turn_ccw()
            direction = -1

def stop_motor():
    global direction
    motor.stop()
    direction = 0

def parse_action(action: dict) -> Action | None:
    # print(action["action"])
    match action["action"]:
        case "pressurize":
            pressure = action["pressure"]
            duration = action["duration"]
            interval = action["check_every"]
            repeats = duration / interval
            _action = ActionTypes.Repeat(
                ActionTypes.Actions(
                    ActionTypes.CallUntilTarget(
                        pressure, 
                        adaptive_motor_speed,
                        graph.get_latest_value,
                        0.25,
                        pressure,
                        motor,
                        graph.get_latest_value,
                        0.25
                    ),
                    ActionTypes.Call(stop_motor),
                    ActionTypes.Delay(interval)
                ),
                repeats
            )
            return _action
        case "wait":
            return ActionTypes.Delay(
                    action["duration"]
                )
        case "repeat":
            previous_action = action_list[-1] if action_list else None
            if previous_action is None or not isinstance(previous_action, Action):
                return None
            return ActionTypes.Repeat(previous_action, int(action["repeats"]))
        case "multiple":
            parsed_actions = []
            for act in action["actions"]:
                parsed_act = parse_action(act)
                if parsed_act is not None:
                    parsed_actions.append(parsed_act)
            return ActionTypes.Actions(*parsed_actions)

def get_action_list(file: str):
    data = read(file)
    for key in data.keys():
        if key == "cycle":
            cycle = data[key]
            if isinstance(cycle, list):
                for action in cycle:
                    act = parse_action(action)
                    if act:
                        action_list.append_action(act)

def read(file: str) -> dict:
    with open(file, "r") as f:
        result = json.load(f)
        # print(f"Got dict by reading {file}:\n{dict}")
        return result

if __name__ == "__main__":
    import argparse
    from serial_helpers import AutoSerial
    import matplotlib.pyplot as plt
    parser = argparse.ArgumentParser()
    parser.add_argument("--pressure_motor_port", "-p")
    parser.add_argument("--arduino_port", "-a")
    parser.add_argument("--file", "-f")
    args = parser.parse_args()

    motor = GoalMotor(AutoSerial(args.pressure_motor_port))
    arduino_serial = AutoSerial(args.arduino_port)
    graph = LiveGraph(50)
    graph.start_animation(get_data_from_arduino(arduino_serial, "pressure"), interval=100)

    get_action_list(args.file)
    motor.actions = action_list
    motor.go()
    plt.show()