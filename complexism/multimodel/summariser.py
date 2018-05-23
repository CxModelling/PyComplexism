from collections import OrderedDict, namedtuple
from complexism.element import Event, Clock
from complexism.mcore import LeafModel, ModelAtom

__author__ = 'TimeWz667'
__all__ = ['Summariser']


class Task:
    def __init__(self, sel, par, name=None):
        self.Selector = sel
        self.Parameter = par
        self.NewName = name if name else '{}@{}'.format(sel, par)

    def __repr__(self):
        return 'Task({}@{}->{})'.format(self.Selector, self.Parameter, self.NewName)

    def to_json(self):
        return {
            'Selector': self.Selector,
            'Parameter': self.Parameter,
            'NewName': self.NewName
        }


class Summariser(ModelAtom):
    def __init__(self, name, dt):
        ModelAtom.__init__(self, name, None)
        self.Clock = Clock(dt)
        self.Tasks = list()
        self.Impulses = OrderedDict()

    def __getitem__(self, item):
        return self.Impulses[item]

    def initialise(self, ti, *args, **kwargs):
        self.Clock.initialise(ti)
        self.Impulses = OrderedDict()

    def reset(self, ti, *args, **kwargs):
        self.Clock.initialise(ti)
        self.Impulses = OrderedDict()

    def find_next(self):
        return Event('Summarise', self.Clock.Next)

    def execute_event(self):
        self.Clock.update(self.TTE)

    def read_tasks(self, mm, ti):
        for tk in self.Tasks:
            self.Impulses[tk.NewName] = mm.select_all(tk.Selector).sum(tk.Parameter, ti)

    def add_task(self, selector, parameter, new_name=None):
        self.Tasks.append(Task(selector, parameter, new_name))

    def clone(self, *args, **kwargs):
        s = Summariser(self.Name, self.Clock.By)
        s.Clock.Initial = self.Clock.Initial
        s.Clock.Last = self.Clock.Last
        s.Tasks = list(self.Tasks)
        return s

    def get_snapshot(self, s, ti):
        return self.Impulses[s]

    def to_json(self):
        return {
            'Tasks': [dict(task) for task in self.Tasks],
            'Timer': self.Clock.to_json()
        }
