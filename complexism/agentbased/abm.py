from abc import ABCMeta, abstractmethod
from collections import namedtuple, OrderedDict
from complexism.mcore import Observer, LeafModel
from complexism.element import Request
from .be import ForeignListener, MultiForeignListener
from .pop import Community


__author__ = 'TimeWz667'
__all__ = ['GenericAgentBasedModel', 'ObsABM', 'AgentBasedModel']

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
    def __init__(self, name, pc, population, obs=None):
        obs = obs if obs else ObsABM()
        LeafModel.__init__(self, name, obs)
        self.PCore = pc
        self.Population = population
        self.Behaviours = OrderedDict()

    def add_observing_event(self, todo):
        self.Obs.Events.append(todo)

    def add_observing_behaviour(self, be):
        if be in self.Behaviours:
            self.Obs.Behaviours.append(be)

    def add_observing_function(self, func):
        self.Obs.add_observing_function(func)

    def add_network(self, net):
        if isinstance(self.Population, Community):
            self.Population.add_network(net)
        else:
            raise AttributeError('The population is not network-based')

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

    @abstractmethod
    def read_y0(self, y0, time):
        pass

    def _make_agent(self, n, time, **kwargs):
        ags = self.Population.add_agent(n, **kwargs)
        for ag in ags:
            for be in self.Behaviours.values():
                be.register(ag, time)

    def preset(self, ti):
        for be in self.Behaviours.values():
            be.initialise(time=ti, model=self)
        for ag in self.Population.Agents.values():
            ag.initialise(time=ti, model=self)

    def reset(self, ti):
        for be in self.Behaviours.values():
            be.reset(time=ti, model=self)
        for ag in self.Population.Agents.values():
            ag.reset(time=ti, model=self)

    def check_enter(self, ag):
        return (be for be in self.Behaviours.values() if be.check_enter(ag))

    def impulse_enter(self, bes, ag, ti):
        for be in bes:
            be.impulse_enter(self, ag, ti)

    def check_exit(self, ag):
        return (be for be in self.Behaviours.values() if be.check_exit(ag))

    def impulse_exit(self, bes, ag, ti):
        for be in bes:
            be.impulse_exit(self, ag, ti)

    def check_pre_change(self, ag):
        return [be.check_pre_change(ag) for be in self.Behaviours.values()]

    def check_post_change(self, ag):
        return [be.check_post_change(ag) for be in self.Behaviours.values()]

    def check_change(self, pre, post):
        bes = list()
        for f, t, be in zip(pre, post, self.Behaviours.values()):
            if be.check_change(f, t):
                bes.append(be)
        return bes

    def impulse_change(self, bes, ag, ti):
        for be in bes:
            be.impulse_change(self, ag, ti)

    def impulse_foreign(self, fore, ti):
        res = False
        for be in self.Behaviours.values():
            if be.check_foreign(fore):
                res = True
                be.impulse_foreign(self, fore, ti)

        if res:
            self.drop_next()
        return res

    def birth(self, n, time, **kwargs):
        ags = self.Population.add_agent(n, **kwargs)
        for ag in ags:
            for be in self.Behaviours.values():
                be.register(ag, time)
            bes = self.check_enter(ag)
            ag.initialise(time)
            self.impulse_enter(bes, ag, time)

        return ags

    def kill(self, i, time):
        ag = self.Population[i]
        bes = self.check_exit(ag)
        self.Population.remove_agent(i)
        self.impulse_exit(bes, ag, time)

    def find_next(self):
        # to be parallel
        for k, be in self.Behaviours.items():
            nxt = be.Next
            self.Requests.append_event(nxt, k, self.Name)

        for k, ag in self.Population.Agents.items():
            nxt = ag.Next
            self.Requests.append_event(nxt, k, self.Name)

    def do_request(self, req: Request):
        nod, evt, time = req.Who, req.Event, req.When
        if nod in self.Behaviours:
            be = self.Behaviours[nod]
            be.fetch_event(evt)
            be.operate(self)
        else:
            ag = self.Population[nod]
            ag.fetch_event(evt)
            pre = self.check_pre_change(ag)
            self.Obs.record(ag, evt, time)
            ag.execute_event()
            ag.drop_next()
            post = self.check_post_change(ag)

            bes = self.check_change(pre, post)
            self.impulse_change(bes, ag, time)

            ag.update_time(time)

    def __len__(self):
        return len(self.Population.Agents)

    @property
    def agents(self):
        return self.Population.Agents.values()


class AgentBasedModel(GenericAgentBasedModel):
    def read_y0(self, y0, time):
        for y in y0:
            try:
                atr = y['attributes']
            except KeyError:
                atr = dict()
            self._make_agent(n=y['n'], time=time, **atr)

    def clone(self, **kwargs):
        pass
