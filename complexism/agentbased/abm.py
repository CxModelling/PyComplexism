from complexism.mcore import Observer, LeafModel
from complexism.element import Request
from .be import ForeignListener, MultiForeignListener
from abc import ABCMeta, abstractmethod
from collections import namedtuple, OrderedDict

__author__ = 'TimeWz667'
__all__ = ['AgentBasedModel']

Record = namedtuple('Record', ('Ag', 'Todo', 'Time'))


class ObsABM(Observer):
    def __init__(self):
        Observer.__init__(self)
        self.Events = list()
        self.Behaviours = list()
        self.Functions = list()
        self.Records = list()

    def add_observing_event(self, todo):
        self.Events.append(todo)

    def add_observing_behaviour(self, beh):
        self.Behaviours.append(beh)

    def add_observing_function(self, func):
        self.Functions.append(func)

    def update_dynamic_observations(self, model, flow, ti):
        for todo in self.Events:
            flow[todo] = sum([rec.Todo == todo for rec in self.Records])
        self.Records.clear()

    def read_statics(self, model, tab, ti):
        for be in self.Behaviours:
            model.Behaviours[be].fill(tab, model, ti)

        for func in self.Functions:
            func(model, tab, ti)

    def record(self, ag, evt, ti):
        self.Records.append(Record(ag.Name, evt.Todo, ti))


class GenericAgentBasedModel(LeafModel, metaclass=ABCMeta):
    def __init__(self, name, pc, population, obs=ObsABM):
        LeafModel.__init__(self, name, obs)
        self.PCore = pc
        self.Population = population
        self.Behaviours = OrderedDict()

    @abstractmethod
    def add_observing_event(self, *args, **kwargs):
        pass

    def add_observing_behaviour(self, be):
        if be.Name not in self.Behaviours:
            self.Behaviours[be.Name] = be

    def add_observing_function(self, func):
        self.Obs.add_observing_function(func)

    def listen(self, mod_src, par_src, par_tar, **kwargs):
        try:
            be = self.Behaviours[par_tar]
            be.set_source(mod_src, par_src)
        except KeyError:
            ForeignListener.decorate(par_tar, self, **kwargs)

    def listen_multi(self, mod_src_all, par_src, par_tar, **kwargs):
        try:
            be = self.Behaviours[par_tar]
            for mod in mod_src_all:
                be.set_source(mod, par_src)
        except KeyError:
            m = MultiForeignListener.decorate(par_tar, self, t_tar=par_tar)
            for mod in mod_src_all:
                m.set_source(mod, par_src)

    def read_y0(self, y0, ti):
        if y0:
            for atr, num in y0.items():
                self.make_agent(atr, num, ti)

    def reset(self, ti):
        for be in self.Behaviours.values():
            be.initialise(self, ti)
        for ag in self.Population.Agents.values():
            ag.initialise(ti)

    def make_agent(self, atr, n, ti):
        ags = self.Population.add_agent(atr, n)
        for ag in ags:
            for be in self.Behaviours.values():
                be.register(ag, ti)

    def check_in(self, ag):
        return (be for be in self.Behaviours.values() if be.check_in(ag))

    def impulse_in(self, bes, ag, ti):
        for be in bes:
            be.impulse_in(self, ag, ti)

    def check_out(self, ag):
        return (be for be in self.Behaviours.values() if be.check_out(ag))

    def impulse_out(self, bes, ag, ti):
        for be in bes:
            be.impulse_out(self, ag, ti)

    def impulse_foreign(self, fore, ti):
        res = False
        for be in self.Behaviours.values():
            if be.check_foreign(fore):
                res = True
                be.impulse_foreign(self, fore, ti)

        if res:
            self.drop_next()
        return res

    def check_tr(self, ag, tr):
        return [be for be in self.Behaviours.values() if be.check_tr(ag, tr)]

    def impulse_tr(self, bes, ag, ti):
        for be in bes:
            be.impulse_tr(self, ag, ti)

    def birth(self, atr, ti, n=1, info=None):
        if info:
            ags = self.Pop.add_agent(atr, n, info=info)
        else:
            ags = self.Pop.add_agent(atr, n)
        for ag in ags:
            for be in self.Behaviours.values():
                be.register(ag, ti)
            bes = self.check_in(ag)
            ag.initialise(ti)
            self.impulse_in(bes, ag, ti)
        return ags

    def kill(self, i, ti):
        ag = self.Pop[i]
        bes = self.check_out(ag)
        self.Pop.remove_agent(i)
        self.impulse_out(bes, ag, ti)

    def find_next(self):
        # to be parallel
        for k, be in self.Behaviours.items():
            nxt = be.next
            self.Requests.append_src(k, nxt, nxt.Time)

        for k, ag in self.Pop.Agents.items():
            nxt = ag.next
            self.Requests.append_src(k, nxt, nxt.Time)

    def do_request(self, req: Request):
        nod, evt, time = req.Node, req.Event, req.Time
        if nod in self.Behaviours:
            be = self.Behaviours[nod]
            be.exec(self, evt)
        else:
            ag = self.Pop[nod]
            tr = evt.Transition
            self.Obs.record(ag, tr, time)
            bes = self.check_tr(ag, tr)
            ag.exec(evt)
            self.impulse_tr(bes, ag, time)
            ag.update(time)

    def __len__(self):
        return len(self.Pop.Agents)

    @property
    def agents(self):
        return self.Pop.Agents.values()

    def clone(self, **kwargs):
        # todo
        return
