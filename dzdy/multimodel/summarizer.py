from dzdy import Event, Clock
from collections import OrderedDict
import pandas as pd

__author__ = 'TimeWz667'


class Summarizer:
    def __init__(self, dt):
        self.Clock = Clock(by=dt)
        self.Nxt = Event.NullEvent
        self.Func = list()
        self.TimeLast = 0
        self.Summary = OrderedDict()

    def initialise(self, ms, ti):
        self.Clock.initialise(ti)
        self.read_obs(ms)
        self.TimeLast = ti
        self.reform_summary()

    @property
    def next(self):
        if self.Nxt is Event.NullEvent:
            self.find_next()
        return self.Nxt

    @property
    def tte(self):
        return self.Nxt.Time

    def find_next(self):
        ti = self.Clock.get_next()
        self.Nxt = Event('Summarizer', ti)

    def summarise(self, ms, evt):
        self.Clock.update(evt.Time)
        self.read_obs(ms)
        self.TimeLast = evt.Time
        self.reform_summary()
        self.drop_next()

    def read_obs(self, ms):
        s = [m.Obs.Last for m in ms.values()]
        s = pd.DataFrame.from_records(s)
        s = s.fillna(0).sum()
        del s['Time']

        self.Summary = s

    def reform_summary(self):
        for f in self.Func:
            f(self.Summary, self.TimeLast)

    def drop_next(self):
        self.Nxt = Event.NullEvent


def reformer_div(name, a, b):
    def f(su, ti):
        su[name] = su[a]/su[b]
    return f
