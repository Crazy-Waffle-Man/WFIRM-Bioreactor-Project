from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent.parent.parent # Parent of parent of this file, should be ../
sys.path.insert(0, str(ROOT)) # Add files from root to path so that we can import from them

from typing import Generator, Any
import json
import time
from serial_helpers import AutoSerial

def get_data_from_arduino(serial: AutoSerial, key: str) -> Generator[Any, None, None]:
    """
    Gets data from arduino running ./pressure_reader.ino
    """
    last_value = None
    while True:
        response: str | None = serial.get_latest_response()
        if response:
            response_dict = {}
            try:
                response_dict = json.loads(response)
            except json.JSONDecodeError as e:
                print(e)
            if key in response_dict:
                last_value = response_dict[key]
                yield last_value
                continue
        # If no response or key missing, yield last known reading or None
        yield last_value
        time.sleep(0.05)

if __name__ == "__main__":
    import live_graph
    import matplotlib.pyplot as plt
    graph = live_graph.LiveGraph(interval=100)
    plt.title("Test graph")
    plt.xlabel("Time")
    plt.ylabel("Pressure (mbar)")
    graph.start_animation(get_data_from_arduino(AutoSerial(input("Port: ")), "pressure"))
    plt.show()