import functools
import time
import pandas as pd
from collections import Counter


__author__ = 'TimeWz667'
__all__ = ['count', 'start_counting', 'stop_counting', 'get_results']


class EventCount:
    def __init__(self, name):
        self.Name = name
        self.Counts = Counter()

    def tick(self, event='Event'):
        self.Counts[event] += 1

    def to_data(self):
        return Counter({'{}:{}'.format(self.Name, k): v for k, v in self.Counts.items()})


class EventCounter:
    ActivateCounter = None
    DefaultCounter = None
    Counters = dict()

    def __init__(self, name):
        self.Name = name
        self.Counts = dict()
        self.Recording = False
        self.TimeStart = None
        self.TimeStop = None
        self.Data = list()

    def __getitem__(self, item):
        try:
            return self.Counts[item]
        except KeyError:
            cnt = EventCount(item)
            self.Counts[item] = cnt
            return cnt

    def start(self):
        self.Recording = True
        self.TimeStart = time.time()
        self.TimeStop = None

    def stop(self):
        if not self.Recording:
            return
        self.Recording = False
        self.TimeStop = time.time()
        dat = dict()
        dat['Counter'] = self.Name
        dat['dT'] = self.TimeStop - self.TimeStart
        cnt = [c.to_data() for c in self.Counts.values()]
        if cnt:
            dat.update(functools.reduce(lambda x, y: x+y, cnt))
        self.Data.append(dat)

    def tick(self, k, event='Event'):
        self[k].tick(event)

    def output(self):
        return pd.DataFrame(self.Data)

    @staticmethod
    def g_start(name=None):
        if EventCounter.ActivateCounter.Recording:
            EventCounter.g_stop()
        if name is not None:
            try:
                cnt = EventCounter.Counters[name]
            except KeyError:
                cnt = EventCounter(name)
                EventCounter.Counters[name] = cnt
        else:
            cnt = EventCounter.DefaultCounter
        EventCounter.ActivateCounter = cnt
        cnt.start()

    @staticmethod
    def g_tick(k, event='Event'):
        cnt = EventCounter.ActivateCounter
        if cnt.Recording:
            cnt.tick(k, event)

    @staticmethod
    def g_stop():
        EventCounter.ActivateCounter.stop()
        EventCounter.ActivateCounter = EventCounter.DefaultCounter


EventCounter.ActivateCounter = EventCounter.DefaultCounter = EventCounter('Default')


start_counting = EventCounter.g_start
stop_counting = EventCounter.g_stop


def get_results(name=None):
    if name is None:
        return EventCounter.DefaultCounter.output()
    else:
        return EventCounter.Counters[name].output()


def count(event='Event'):
    def count_decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            EventCounter.g_tick(self.Name, event)
            return result

        return wrapper
    return count_decorator


if __name__ == '__main__':
    class Model:
        def __init__(self, name):
            self.Name = name

        @count('A')
        def do_a(self):
            pass

        @count('B')
        def do_b(self):
            pass

        @count()
        def do_c(self):
            pass

    start_counting()
    m = Model('test')

    for _ in range(100):
        m.do_a()

    for _ in range(200):
        m.do_b()

    m.do_c()
    stop_counting()
    print(get_results())
