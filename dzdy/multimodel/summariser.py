from dzdy import Event, Clock, LeafModel, ModelSelector
from collections import OrderedDict, namedtuple
import pandas as pd

__author__ = 'TimeWz667'
__all__ = ['Summariser']


class Summariser(LeafModel):
    def __init__(self, dt):
        LeafModel.__init__(self, 'Summary', None)
        self.Clock = Clock(by=dt)
        self.Nxt = Event.NullEvent
        self.Tasks = list()  # (selector, parameters, new name)
        self.Summary = OrderedDict()

    def find_next(self):
        ti = self.Clock.get_next()
        self.Nxt = Event(self.Name, ti)

    def clone(self, **kwargs):
        s = Summariser(self.Clock.By)
        s.TimeEnd = self.TimeEnd
        s.Clock.Initial = self.Clock.Initial
        s.Clock.Last = self.Clock.Last
        s.Tasks = list(self.Tasks)
        return s

    def reset(self, ti):
        self.Clock.initialise(ti)
        self.Nxt = Event.NullEvent
        self.Summary = OrderedDict()

    def summarise(self, ms, evt):
        self.Clock.update(evt.Time)
        self.read_obs(ms)
        self.TimeEnd = evt.Time
        self.drop_next()

    def read_obs(self, ms):
        tasks = dict()
        for sc, sp, tar in self.Tasks:
            if sc in tasks:
                tasks[sc].append((sp, tar))
            else:
                tasks[sc] = [(sp, tar)]

        s = OrderedDict()
        for k, vs in tasks.items():
            ms.select_all(k)
            for (sp, tar) in vs:
                s[tar] = ms.extract(sp).sum()

        self.Summary = s

    def do_request(self, req):
        self.Clock.update(req.Time)

    def listen(self, src_model, src_value, par_target):
        if not par_target:
            if src_model == '*':
                par_target = src_value
            else:
                par_target = '{}@{}'.format(src_model, src_value)
        self.Tasks.append((src_model, src_model, par_target))
