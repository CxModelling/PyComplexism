from complexism.element import Event
from complexism.agentbased import GenericAgent
from .modifier import ModifierSet


__author__ = 'TimeWz667'
__all__ = ['StSpAgent']


class StSpAgent(GenericAgent):
    def __init__(self, name, st, pars=None):
        GenericAgent.__init__(self, name, pars)
        self.State = st
        self.Transitions = dict()
        self.Modifiers = ModifierSet()

    def __getitem__(self, item):
        try:
            return GenericAgent.__getitem__(self, item)
        except KeyError as e:
            if item == 'State':
                return self.State
            else:
                raise e

    def initialise(self, ti=0, *args, **kwargs):
        self.Transitions.clear()
        self.update_time(ti)

    def reset(self, ti=0, *args, **kwargs):
        self.Transitions.clear()
        self.update_time(ti)

    def find_next(self):
        if self.Transitions:
            tr, ti = min(self.Transitions.items(), key=lambda x: x[1])
            return Event(tr, ti, tr.Name)
        else:
            return Event.NullEvent

    def execute_event(self):
        nxt = self.Next
        if nxt is not Event.NullEvent:
            self.State = self.State.execute(nxt)

    def update_time(self, ti):
        self.Transitions = {k: v for k, v in self.Transitions.items() if v >= ti}
        new_trs = self.State.next_transitions()
        ad = list(set(new_trs) - set(self.Transitions.keys()))
        self.Transitions = {k: v for k, v in self.Transitions.items() if k in new_trs}
        for tr in ad:
            tte = tr.rand(self.Parameters) # verify
            for mo in self.Modifiers.on(tr):
                tte = mo.modify(tte)
            self.Transitions[tr] = tte + ti
        self.drop_next()

    def add_modifier(self, mod):
        """
        Append a modifier
        :param mod:
        :type mod: Modifier
        """
        self.Modifiers[mod.Name] = mod

    def shock(self, ti, source, target, value):
        """
        Make an impulse on a modifier
        :param ti: time
        :type ti: float
        :param source: source of impulse, None for state space model
        :type source: str
        :param target: target modifier
        :type target: str
        :param value: value of impulse
        """
        mod = self.Modifiers[target]
        if mod.update(value):
            self.modify(target, ti)

    def get_mod_value(self, m):
        return self.Modifiers[m].Value

    def set_mod_value(self, m, value):
        mod = self.Modifiers[m]
        mod.Value = value

    def modify(self, m, ti):
        """
        Re-modify a transition via modifier m
        :param m: target modifier
        :type m: str
        :param ti: time
        :type ti: float
        """
        mod = self.Modifiers[m]
        if mod.Target in self.Transitions:
            tr = mod.Target
            tte = tr.rand(self.Parameters, **self.Attributes)
            for mo in self.Modifiers.on(tr):
                tte = mo.modify(tte)
            self.Transitions[tr] = tte + ti
            self.drop_next()

    def isa(self, st):
        return st in self

    def __contains__(self, st):
        return st in self.State

    def clone(self, dc_new=None):
        if dc_new:
            ag_new = StSpAgent(self.Name, dc_new[self.State.Name])
            for tr, tte in self.Transitions.items():
                ag_new.Transitions[dc_new.Transitions[tr.Name]] = tte
        else:
            ag_new = StSpAgent(self.Name, self.State)

        ag_new.Attributes.update(self.Attributes)
        return ag_new

    def to_json(self):
        js = GenericAgent.to_json(self)
        js['State'] = self.State.Name
        js['Transitions'] = {tr.Name: tte for tr, tte in self.Transitions.items()}
        js['Modifiers'] = self.Modifiers.to_json()
        return js

    def to_snapshot(self):
        js = GenericAgent.to_json(self)
        js['State'] = self.State.Name
        return js

    def to_data(self):
        dat = GenericAgent.to_data(self)
        dat['State'] = self.State.Name
        return dat
