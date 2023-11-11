import threading


# Custom class used to allow Threads to have result
# Reference https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread
class ThreadWithResult(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        self.result = None

        def function():
            self.result = target(*args, **kwargs)
        super().__init__(group=group, target=function, name=name, daemon=daemon)
