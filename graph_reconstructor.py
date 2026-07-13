import tkinter as tk
from tkinter import filedialog
import datetime
import matplotlib.pyplot as plt

import live_graph

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(defaultextension=".log", initialdir="./logging")

if not file_path:
    raise SystemExit("No log file selected.")

with open(file_path, "r") as f:
    lines = f.read().splitlines()

if not lines:
    raise ValueError("Selected log file is empty.")

first_line = lines[0]
file_name = first_line.replace("\\", "/").split("/")[-1]
start_time = first_line.removeprefix("Datalogging for the LiveGraph, starting at ")[0:19]
title = f"{file_name}, {start_time}"

def read(lines):
    for line in lines[1:]:
        if not line.strip():
            continue

        data = line.split(": ", 1)
        if len(data) != 2:
            continue

        timestamp_text, value_text = data
        y = float(value_text)
        time = datetime.datetime.strptime(timestamp_text, "%Y-%m-%d@%H:%M:%S.%f").timestamp()
        yield y, time

graph = live_graph.LiveGraph(maxlen=None, logging=False, override_x_data=True, interval=20)
graph.set_title(title)
graph.set_xlabel("Time")
graph.set_ylabel("Value")
graph.start_animation(read(lines))

plt.show()
