import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D
from matplotlib.figure import Figure
import time
from collections import deque

class LiveGraph:
    def __init__(self, maxlen: int = 50, interval: int = 1000):
        """
        Create a live-updating graph with up to `maxlen` data points that updates every `interval` ms.
        """
        self.time_values = deque([], maxlen)
        self.y_values = deque([], maxlen)
        self.fig, self.ax = plt.subplots()
        # create an empty Line2D so we can update its data later
        self.line, = self.ax.plot([], [], lw=2, color="blue")
        # don't start an automatic animation by default; updates happen when `update` is called
        self.animation = None
        # default interval for animation (ms)
        self.interval = interval
        self.widget = None
    
    @property
    def latest_value(self):
        return self.y_values[-1] if self.y_values else None
    def get_latest_value(self):
        return self.latest_value
    def set_title(self, title: str) -> None:
        self.ax.set_title(title)

    def set_xlabel(self, label: str) -> None:
        self.ax.set_xlabel(label)

    def set_ylabel(self, label: str) -> None:
        self.ax.set_ylabel(label)

    def get_widget(self, parent=None, title: str | None = None, xlabel: str | None = None, ylabel: str | None = None):
        """Return the FigureCanvas widget. Optionally set title and axis labels on the figure.

        When embedding the canvas in a GUI, prefer passing `title`, `xlabel` and `ylabel`
        here so the labels are applied to this figure's Axes instead of the global `plt`.
        """
        if title is not None:
            self.set_title(title)
        if xlabel is not None:
            self.set_xlabel(xlabel)
        if ylabel is not None:
            self.set_ylabel(ylabel)

        if self.widget is None:
            self.widget = FigureCanvas(self.fig)
            if parent is not None:
                self.widget.setParent(parent)
        return self.widget

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
        # record current time and store relative time (seconds since first update)
        now = time.time()
        if not hasattr(self, "start_time") or self.start_time is None:
            self.start_time = now
        rel_time = now - self.start_time

        # append a single timestamp and value
        self.time_values.append(rel_time)
        self.y_values.append(y_value)

        # convert absolute times to relative times from the latest sample
        max_time = max(self.time_values)
        x_values = [t - max_time for t in self.time_values]

        # Next 8 lines are O(2n) for both self.x_values and self.y_values
        minx = min(x_values)
        maxx = max(x_values)
        miny = min(self.y_values)
        maxy = max(self.y_values)
        if minx != maxx:
            self.ax.set_xlim(minx, maxx)
        if miny != maxy:
            self.ax.set_ylim(miny, maxy)

        # update the plotted line and redraw
        self.line.set_data(x_values, list(self.y_values))
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