from typing import Iterable, Callable
import time
import serial_helpers
from live_graph import LiveGraph
from threading import Thread

class GoalMotor(serial_helpers.ESI_MP2):
    def __init__(self, serial: serial_helpers.AutoSerial):
        super().__init__(serial)
        self.actions: ActionList
    def _update(self):
        while True:
            self.actions.exec()
    def go(self):
        thread = Thread(target=self._update, daemon=True) # Don't block main thread from exiting
        thread.start()

class Action: # abstract
    def exec(self) -> None:
        ...

class ActionTypes:
    class Actions(Action):
        def __init__(self, *args) -> None:
            self.actions = args
        def exec(self):
            # print("Executing multiple actions...")
            for action in self.actions:
                if isinstance(action, Action):
                    action.exec()
                else:
                    raise ValueError(f"ActionList expects to only be populated with Action objects. Found {type(action)} instead.")
    class Repeat(Action):
        def __init__(self, action: Action, repeats: int) -> None:
            self.repeats = repeats
            self.action = action
        def exec(self):
            # print(f"Executing repeat action...")
            for i in range(self.repeats):
                self.action.exec()
    class Delay(Action):
        def __init__(self, millis: float) -> None:
            self.delay = millis / 1000
        def exec(self):
            # print("Executing Delay action")
            time.sleep(self.delay)
    class CallUntilTarget(Action):
        def __init__(self, target: int | float, func: Callable, current_value_getter: Callable, tolerance: float = 0, *args) -> None:
            """
            Call `func(*args)` repeatedly until `target - tolerance <= current_value_getter() <= target + tolerance`
            """
            self.lower = target - tolerance
            self.upper = target + tolerance
            self.func = func
            self.getter = current_value_getter
            self.args = args
        def exec(self):
            # print("Executing CallUntilTarget")
            while not (self.getter() >= self.lower and self.getter() <= self.upper):
                self.func(*self.args)
    class Call(Action):
        def __init__(self, func: Callable, *args):
            self.func = func
            self.args = args
        def exec(self) -> None:
            self.func(*self.args)
                

class ActionList(list):
    def __init__(self, iterable: Iterable) -> None:
        super().__init__([item for item in iterable if item is Action])
    def exec(self):
        for action in self:
            if isinstance(action, Action):
                action.exec()
            else:
                raise ValueError(f"ActionList expects to only be populated with Action objects. Found {type(action)} instead.")
    def append_action(self, action: Action):
        self.append(action)
        return self # Make it chainable