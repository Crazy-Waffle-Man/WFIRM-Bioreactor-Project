from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent.parent.parent # Parent of parent of this file, should be ../
sys.path.insert(0, str(ROOT)) # Add files from root to path so that we can import from them

from typing import Generator, Any
import json
from serial_helpers import AutoSerial

def get_data_from_arduino(serial: AutoSerial, key: str) -> Generator[dict[str, Any]]:
    """
    Gets data from arduino running ./pid/pid.ino
    """
    while True:
        response: str | None = serial.get_response()
        if response:
            print(json.loads(response))
            print(json.loads(response)[key])
            yield json.loads(response)[key]

if __name__ == "__main__":
    import live_graph
    import matplotlib.pyplot as plt
    graph = live_graph.LiveGraph()
    plt.title("Test graph")
    plt.xlabel("Time")
    plt.ylabel("Pressure (mbar)")
    graph.start_animation(get_data_from_arduino(AutoSerial(input("Port: ")), "pressure"))
    plt.show()