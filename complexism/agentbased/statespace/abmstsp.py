from complexism.dcore import Transition
from complexism.agentbased.abm import GenericAgentBasedModel, ObsABM
from collections import namedtuple, Counter

__author__ = 'TimeWz667'
__all__ = ['StSpAgentBasedModel']

Record = namedtuple('Record', ('Ag', 'Todo', 'Time'))


class ObsStSpABM(ObsABM):
    def __init__(self):
        ObsABM.__init__(self)
        self.States = list()
        self.Transitions = list()

    def add_observing_state(self, st):
        self.States.append(st)

    def add_observing_transition(self, tr):
        self.Transitions.append(tr)

    def update_dynamic_observations(self, model, flow, ti):
        tds = [rec.Todo for rec in self.Records]
        count = Counter(tds)
        trs = {k: v for k, v in count.items() if isinstance(k, Transition)}
        es = {k: v for k, v in count.items() if not isinstance(k, Transition)}

        for tr in self.Transitions:
            try:
                flow[tr.Name] = trs[tr]
            except KeyError:
                flow[tr.Name] = 0

        for evt in self.Events:
            try:
                flow[str(evt)] = es[evt]
            except KeyError:
                flow[str(evt)] = 0

        self.Records.clear()

    def read_statics(self, model, tab, ti):
        ObsABM.read_statics(self, model, tab, ti)

        pop = model.Population
        for st in self.States:
            tab[st] = pop.count(st=st)

        for be in self.Behaviours:
            model.Behaviours[be].fill(tab, model, ti)

        for fn in self.Functions:
            fn(model, tab, ti)

    def record(self, ag, evt, ti):
        self.Records.append(Record(ag.Name, evt.Todo, ti))


class StSpAgentBasedModel(GenericAgentBasedModel):
    def __init__(self, name, pc, population):
        GenericAgentBasedModel.__init__(self, name, pc, population, ObsStSpABM())
        self.DCore = population.Eve.DCore

    def read_y0(self, y0, ti):
        for y in y0:
            try:
                atr = y['attributes']
            except KeyError:
                atr = dict()
            self._make_agent(n=y['n'], ti=ti, **atr)

    def add_observing_transition(self, tr):
        try:
            tr = self.DCore.Transitions[tr]
        except KeyError:
            raise KeyError('Transition {} does not exist'.format(tr))
        self.Observer.add_observing_transition(tr)

    def add_observing_state(self, st):
        if st in self.DCore.States:
            self.Observer.add_observing_state(st)
        else:
            raise KeyError('State {} does not exist'.format(st))

    def listen(self, mod_src, message, par_src, par_tar, **kwargs):
        try:
            be = self.Behaviours[par_tar]
            be.set_source(mod_src, message, par_src)
        except KeyError:
            # name = par_tar
            name = '{}-{}'.format(par_src, par_tar)
            #ForeignShock.decorate(name, self, mod_src=mod_src, message=message, par_src=par_src, t_tar=par_tar, **kwargs)

    def clone(self, **kwargs):
        pass
