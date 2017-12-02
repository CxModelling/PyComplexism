from dzdy import Request, Clock, LeafModel
from collections import OrderedDict, namedtuple

__author__ = 'TimeWz667'
__all__ = ['Summariser']


Task = namedtuple('Task', ('Selector', 'Parameter', 'NewName'))


class Summariser(LeafModel):
    def __init__(self, name, dt):
        LeafModel.__init__(self, name, None)
        self.Clock = Clock(dt=dt)
        self.Tasks = list()
        self.Employer = None
        self.Impulses = OrderedDict()

    def find_next(self):
        self.Requests.append(Request('Summary', self.Clock.Next))

    def __getitem__(self, item):
        try:
            return self.Impulses[item]
        except KeyError:
            return 0

    def clone(self, **kwargs):
        s = Summariser(self.Name, self.Clock.By)
        s.Clock.Initial = self.Clock.Initial
        s.Clock.Last = self.Clock.Last
        s.Tasks = list(self.Tasks)
        return s

    def reset(self, ti):
        self.Clock.initialise(ti)
        self.Impulses = OrderedDict()

    def read_tasks(self):
        for tk in self.Tasks:
            self.Impulses[tk.NewName] = \
                self.Employer.select_all(tk.Selector).sum(tk.Parameter)

    def do_request(self, req):
        self.Clock.update(req.Time)
        self.TimeEnd = req.Time

    def listen(self, src_model, src_value, par_target):
        if not par_target:
            if src_model == '*':
                par_target = src_value
            else:
                par_target = '{}@{}'.format(src_model, src_value)
        self.Tasks.append(Task(src_model, src_value, par_target))

    def to_json(self):
        return {
            'Tasks': [dict(task) for task in self.Tasks],
            'Timer': self.Clock.to_json()
        }
