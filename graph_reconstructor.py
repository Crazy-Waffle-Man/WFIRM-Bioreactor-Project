import tkinter as tk
from tkinter import filedialog
import datetime

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(defaultextension=".log",initialdir="./logging")

import matplotlib.pyplot as plt

fig, ax = plt.subplots()
time_data = []
y_data = []

with open(file_path, "r") as f:
    lines = f.read().splitlines()
    for line in lines:
        if line == lines[0]:
            file = line.replace("\\", "/").split("/")[-1] # last of filepath
            print(file)
            time = line.removeprefix("Datalogging for the LiveGraph, starting at ")[0:19]
            plt.title(f"{file}, {time}")
        else:
            data = line.split(": ")
            y_data.append(float(data[-1]))
            time = datetime.datetime.strptime(data[0], "%Y-%m-%d@%H:%M:%S.%f")
            time_data.append(time)

line = ax.plot(time_data, y_data, lw = 2, color="blue")

plt.show()
