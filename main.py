import live_graph
import sensirion.i2c_data_getter

import matplotlib.pyplot as plt

graph = live_graph.LiveGraph(interval=100)
plt.title("Flow rate vs time")
plt.xlabel("Time (s)")
plt.ylabel("Flow rate (mL/min)")
# start live animation using the default random generator
graph.start_animation(sensirion.i2c_data_getter.read_data_from_sensor())
plt.show()