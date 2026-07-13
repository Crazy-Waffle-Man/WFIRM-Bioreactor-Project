import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as mdates
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D
from collections import deque
from threading import Lock
from datetime import datetime

class LiveGraph:
    def __init__(self, maxlen: int | None = 50, interval: int = 1000, logging: bool = False, override_x_data=False):
        """
        Create a live-updating graph with up to `maxlen` data points that updates every `interval` ms.
        """
        self.values: list[tuple[str, float | int]] = []
        self.time_values: deque[float] = deque([], maxlen)
        self.override_x_data = override_x_data
        self.y_values: deque[float] = deque([], maxlen)
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], lw=2, color="blue")
        self.animation = None
        self.interval = interval
        self.widget = None
        self.lock = Lock()

        now = datetime.now()
        self.file = now.strftime("logging/%Y-%m-%d_%H-%M-%S.log")
        self.logging = logging

        if self.logging:
            try:
                import inspect
                caller = inspect.stack()[1]
                with open(self.file, "x") as file:
                    file.write(f"Datalogging for the LiveGraph, starting at {now.strftime('%Y-%m-%d %H:%M:%S')} while running {caller.filename}\n")
            except FileExistsError:
                print(f"Somehow, it has been this time before. Failed to create log file {self.file}")
            except FileNotFoundError:
                from os import mkdir
                mkdir("logging")
                import inspect
                caller = inspect.stack()[1]
                with open(self.file, "x") as file:
                    file.write(f"Datalogging for the LiveGraph, starting at {now.strftime('%Y-%m-%d %H:%M:%S')} while running {caller.filename}\n")

    @property
    def latest_value(self):
        with self.lock:
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
        """Return the FigureCanvas widget. Optionally set title and axis labels on the figure."""
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
        """Start a live `FuncAnimation` that calls `update()` for each frame."""
        if frames is None:
            def _default_gen():
                from random import randint
                while True:
                    yield randint(0, 50)
            frames = _default_gen()

        if interval is None:
            interval = self.interval

        def _update(y: int | float | tuple):
            if isinstance(y, tuple):
                self.update(*y)
            else:
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

    def update(self, y_value: int | float | None, x_value: int | float | None = None) -> Line2D:
        if y_value is None:
            return self.line

        now = datetime.now()
        if self.override_x_data:
            rel_time = x_value if x_value is not None else now.timestamp()
        else:
            ts = now.timestamp()
            if not hasattr(self, "start_time") or self.start_time is None:
                self.start_time = ts
            rel_time = ts - self.start_time

        with self.lock:
            self.time_values.append(float(rel_time))
            self.y_values.append(float(y_value))

            if self.logging:
                self.values.append((now.strftime("%Y-%m-%d@%H:%M:%S.%f")[:-3], y_value))

            if len(self.values) >= 50:
                if self.logging:
                    with open(self.file, "a") as file:
                        for value in self.values:
                            file.write(f"{value[0]}: {value[1]}\n")
                self.values = []

        time_values = list(self.time_values)

        if self.override_x_data:
            x_plot_values: list[datetime | float] = [
                datetime.fromtimestamp(t) if isinstance(t, (int, float)) else t
                for t in time_values
            ]
        else:
            if time_values:
                start_time = time_values[0]
                x_plot_values = [t - start_time for t in time_values]
            else:
                x_plot_values = []

        y_plot_values = list(self.y_values)

        if x_plot_values:
            minx = min(x_plot_values)
            maxx = max(x_plot_values)
            if minx != maxx:
                self.ax.set_xlim(minx, maxx) # type: ignore

            if self.override_x_data:
                self.ax.xaxis_date()
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M:%S"))
        else:
            minx = maxx = None

        miny = min(y_plot_values)
        maxy = max(y_plot_values)
        if miny != maxy:
            if maxy - miny < 1:
                mean = (miny + maxy) / 2
                self.ax.set_ylim(mean - 0.5, mean + 0.5)
            else:
                self.ax.set_ylim(miny, maxy)

        self.line.set_data(x_plot_values, y_plot_values) # type: ignore
        try:
            self.fig.canvas.draw_idle()
        except Exception:
            self.fig.canvas.draw()
        return self.line


if __name__ == "__main__":
    graph = LiveGraph(interval=100, logging=True)
    plt.title("Test graph")
    plt.xlabel("Time")
    plt.ylabel("Random values")
    graph.start_animation()
    plt.show()