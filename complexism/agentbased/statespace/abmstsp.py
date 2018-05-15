from complexism.dcore import Transition
from complexism.mcore import Observer
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

        for k, v in count.items():
            if isinstance(k, Transition):
                if k in self.Transitions:
                    flow[k.Name] = v
            else:
                if k in self.Events:
                    flow[str(k)] = v

        self.Records.clear()

    def read_statics(self, model, tab, ti):
        ObsABM.read_statics(self, model, tab, ti)

        pop = model.Population
        for st in self.States:
            tab[st] = pop.count(st=st)

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
        self.Obs.add_observing_transition(tr)

    def add_observing_state(self, st):
        if st in self.DCore.States:
            self.Obs.add_observing_state(st)
        else:
            raise KeyError('State {} does not exist'.format(st))

    def listen(self, mod_src, par_src, par_tar, **kwargs):
        pass

    def listen_multi(self, mod_src_all, par_src, par_tar, **kwargs):
        pass

    def clone(self, **kwargs):
        pass
