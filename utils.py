
import threading


def fireandforget(func):
    def threadwrapped(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.start()
    return threadwrapped
