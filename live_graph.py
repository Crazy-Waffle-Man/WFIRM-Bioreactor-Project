import matplotlib.pyplot as plt
import matplotlib.animation

class LiveGraph:
    def __init__(self, title: str="Live Graph", xlabel: str="X-axis", ylabel: str="Y-axis", refresh_rate: int = 1000):
        self.title: str = title
        self.xlabel: str = xlabel
        self.ylabel: str = ylabel
        self.xdata: list[int | float]= []
        self.ydata: list[int | float] = []
        self.figure = plt.figure()
        self.axes = self.figure.add_subplot()
        self.animation = matplotlib.animation.FuncAnimation(self.figure, self._animate, interval = refresh_rate)
    
    def update_data(self, x: int | float, y: int | float):
        self.xdata.append(x)
        self.ydata.append(y)

    def _animate(self, i):
        self.axes.clear()
        self.axes.plot(self.xdata, self.ydata)
    
    def show(self):
        plt.show()