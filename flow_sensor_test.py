import live_graph
import sensirion.i2c_data_getter

import matplotlib.pyplot as plt
from time import sleep

port = input("Flow sensor port: ")
graph = live_graph.LiveGraph(interval=100)
plt.title("Flow rate vs time")
plt.xlabel("Time (s)")
plt.ylabel("Flow rate (mL/min)")
# start live animation using the default random generator
generator = sensirion.i2c_data_getter.read_data_from_flow_sensor(port)
sleep(5)
graph.start_animation(generator)
plt.show()