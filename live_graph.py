import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
import time
from collections import deque

class LiveGraph:
    def __init__(self, maxlen: int = 50, interval: int = 1000):
        """
        Create a live-updating graph with up to `maxlen` data points that updates every `interval` ms.
        """
        self.x_values = deque([], maxlen)
        self.y_values = deque([], maxlen)
        self.fig, self.ax = plt.subplots()
        # create an empty Line2D so we can update its data later
        self.line, = self.ax.plot([], [], lw=2, color="blue")
        # don't start an automatic animation by default; updates happen when `update` is called
        self.animation = None
        # default interval for animation (ms)
        self.interval = interval

    def start_animation(self, frames=None, interval: int | None = None):
        """Start a live `FuncAnimation` that calls `update()` for each frame.

        - `frames` may be any iterable/generator producing y-values. If omitted,
          a simple random integer generator is used for demonstration.
        - `interval` overrides the instance default interval (in ms).
        Returns the created `FuncAnimation`.
        """
        if frames is None:
            def _default_gen():
                from random import randint
                while True:
                    yield randint(0, 50)
            frames = _default_gen()
        if interval is None:
            interval = self.interval
        # animation will call our update(frame) where frame is a y-value
        def _update(y: int | float):
            self.update(y)
        self.animation = animation.FuncAnimation(
            self.fig,
            lambda y: _update(y),
            frames=frames,
            interval=interval,
            blit=False,
            cache_frame_data=False,
        )
        return self.animation
    
    def update(self, y_value: int | float) -> Line2D:
        start_time = time.time()
        # TODO: make self.x_values relative to start_time, i.e. display past data points as -n*interval
        self.x_values.append(start_time)
        self.y_values.append(y_value)
        # Next 8 lines are O(2n) for both self.x_values and self.y_values
        minx = min(self.x_values)
        maxx = max(self.x_values)
        miny = min(self.y_values)
        maxy = max(self.y_values)
        if minx != maxx:
            self.ax.set_xlim(minx, maxx)
        if miny != maxy:
            self.ax.set_ylim(miny, maxy)

        # update the plotted line and redraw
        self.line.set_data(list(self.x_values), list(self.y_values))
        try:
            self.fig.canvas.draw_idle()
        except Exception:
            self.fig.canvas.draw()
        return self.line

if __name__ == "__main__":
    graph = LiveGraph(interval=100)
    plt.title("Test graph")
    plt.xlabel("Time")
    plt.ylabel("Random values")
    # start live animation using the default random generator
    graph.start_animation()
    plt.show()