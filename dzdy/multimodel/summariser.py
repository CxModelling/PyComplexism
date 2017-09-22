from dzdy import Request, Clock, LeafModel
from collections import OrderedDict

__author__ = 'TimeWz667'
__all__ = ['Summariser']


class Summariser(LeafModel):
    def __init__(self, name, dt):
        LeafModel.__init__(self, name, None)
        self.Clock = Clock(by=dt)
        self.Tasks = list()  # (selector, parameters, new name)
        self.Summary = OrderedDict()

    def find_next(self):
        self.Requests.append(Request('Summary', self.Clock.get_next()))

    def __getitem__(self, item):
        try:
            return self.Summary[item]
        except KeyError:
            return 0

    def clone(self, **kwargs):
        s = Summariser(self.Name, self.Clock.By)
        s.TimeEnd = self.TimeEnd
        s.Clock.Initial = self.Clock.Initial
        s.Clock.Last = self.Clock.Last
        s.Tasks = list(self.Tasks)
        return s

    def reset(self, ti):
        self.Clock.initialise(ti, ti)
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
            sel = ms.select_all(k)
            for (sp, tar) in vs:
                s[tar] = sel.extract(sp).sum()

        self.Summary = s

    def do_request(self, req):
        self.Clock.update(req.Time)
        self.TimeEnd = req.Time

    def listen(self, src_model, src_value, par_target):
        if not par_target:
            if src_model == '*':
                par_target = src_value
            else:
                par_target = '{}@{}'.format(src_model, src_value)
        self.Tasks.append((src_model, src_value, par_target))
