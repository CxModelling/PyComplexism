from complexism.element import Event
from complexism.abmodel import ModifierSet, GenericAgent

__author__ = 'TimeWz667'
__all__ = ['StSpAgent']


class StSpAgent(GenericAgent):
    def __init__(self, name, st):
        GenericAgent.__init__(self, name)
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

    def initialise(self, time=0, **kwargs):
        self.Transitions.clear()
        self.update_time(time)

    def reset(self, time=0, *args, **kwargs):
        self.Transitions.clear()
        self.update_time(time)

    def find_next(self):
        if self.Transitions:
            return Event(*min(self.Transitions.items(), key=lambda x: x[1]))
        else:
            return Event.NullEvent

    def execute_event(self):
        nxt = self.Next
        if nxt is not Event.NullEvent:
            self.State = self.State.execute(nxt)

    def update_time(self, time):
        new_trs = self.State.next_transitions()
        ad = list(set(new_trs) - set(self.Transitions.keys()))
        self.Transitions = {k: v for k, v in self.Transitions.items() if k in new_trs}
        for tr in ad:
            tte = tr.rand(self)
            for mo in self.Modifiers.on(tr):
                tte = mo.modify(tte)
            self.Transitions[tr] = tte + time
        self.drop_next()

    def add_modifier(self, mod):
        """
        Append a modifier
        :param mod:
        :type mod: Modifier
        """
        self.Modifiers[mod.Name] = mod

    def shock(self, time, source, target, value):
        """
        Make an impulse on a modifier
        :param time: time
        :type time: float
        :param source: source of impulse, None for state space model
        :type source: str
        :param target: target modifier
        :type target: str
        :param value: value of impulse
        """
        mod = self.Modifiers[target]
        if mod.update(value):
            self.modify(target, time)

    def modify(self, m, time):
        """
        Re-modify a transition via modifier m
        :param m: target modifier
        :type m: str
        :param time: time
        :type time: float
        """
        mod = self.Modifiers[m]
        if mod.target in self.Transitions:
            tr = mod.target
            tte = tr.rand()
            for mo in self.Modifiers.on(tr):
                tte = mo.modify(tte)
            self.Transitions[tr] = tte + time
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


class AgentOld:
    def __init__(self, i, st):
        self.Name = i
        self.Info = dict()
        self.State = st
        self.Trans = dict()  # Transition -> time
        self.Mods = ModifierSet()
        self.Next = Event.NullEvent

    def __getitem__(self, item):
        try:
            return self.Info[item]
        except KeyError:
            if item == 'State':
                return self.State
            else:
                raise KeyError('No this attribute')

    def __setitem__(self, key, value):
        self.Info[key] = value

    def update_info(self, info, force=True):
        for k, v in info.items():
            if k not in self.Info or force:
                self.Info[k] = v

    @property
    def next(self):
        if self.Next is Event.NullEvent:
            self.Next = self.find_next()
        return self.Next

    @property
    def tte(self):
        return self.next.Time

    def find_next(self):
        if self.Trans:
            return Event(*min(self.Trans.items(), key=lambda x: x[1]))
        else:
            return Event.NullEvent

    def drop_next(self):
        self.Next = Event.NullEvent

    def add_mod(self, mod):
        self.Mods[mod.Name] = mod

    def initialise(self, ti):
        self.Trans.clear()
        self.update(ti)

    def assign(self, evt):
        """
        Assign an event which is ready to be executed
        Args:
            evt: event

        """
        self.Next = evt

    def exec(self, evt):
        """
        Execute an event directly
        Args:
            evt: event

        """
        if evt is not Event.NullEvent:
            self.State = self.State.exec(evt.Transition)

    def update(self, ti):
        """
        Update time to event of all transitions. Ingnore the transitions which does exist in the previous state
        Args:
            ti: time

        """
        new_trs = self.State.next_transitions()
        ad = list(set(new_trs) - set(self.Trans.keys()))
        self.Trans = {k: v for k, v in self.Trans.items() if k in new_trs}
        for tr in ad:
            tte = tr.rand()
            for mo in self.Mods.on(tr):
                tte = mo.modify(tte)
            self.Trans[tr] = tte + ti
        self.drop_next()

    def shock(self, m: str, val: float, ti: float):
        """
        Make a impulse on a modifier
        Args:
            m: target modifier
            val: new value
            ti: time

        """
        mod = self.Mods[m]
        if mod.update(val):
            self.modify(m, ti)

    def modify(self, m, ti):
        """
        Re-modify a transition via modifier m
        Args:
            m: target modifier
            ti: time

        """
        mod = self.Mods[m]
        if mod.target in self.Trans:
            tr = mod.target
            tte = tr.rand()
            for mo in self.Mods.on(tr):
                tte = mo.modify(tte)
            self.Trans[tr] = tte + ti
            self.drop_next()

    def isa(self, atr):
        return atr in self

    def has_info(self, s):
        return s in self.Info

    def match(self, info):
        for k, v in info.items():
            if self.Info[k] != v:
                return False
        return True

    def __contains__(self, st):
        return st in self.State

    def __repr__(self):
        s = 'ID: {}, '.format(self.Name)
        if self.Info:
            s += ', '.join([str(k) + ': ' + str(v) for k, v in self.Info.items()])
            s += ', '
        s += 'State: ' + str(self.State.Name)
        return s

    @property
    def detail(self):
        nxt = self.next
        trs = '\n'.join('\t{}@{}{}'.format(k, v, '*' if k is nxt else '') for k, v in self.Trans.items())
        info = '\n'.join('{}: {}'.format(k, v) for k, v in self.Info.items())
        return 'ID: {}\nState: {}\n{}\n\nTransitions:\n{}'.format(self.Name, self.State, info, trs)

    def clone(self, dc_new=None, tr_ch=None):
        if dc_new:
            ag_new = Agent(self.Name, dc_new[self.State.Name])
            if tr_ch:
                for tr, tte in self.Trans.items():
                    if tr.Name in tr_ch:
                        continue
                    ag_new.Trans[dc_new.Transitions[tr.Name]] = tte
            else:
                for tr, tte in self.Trans.items():
                    ag_new.Trans[dc_new.Transitions[tr.Name]] = tte

        else:
            ag_new = Agent(self.Name, self.State)

        ag_new.Info.update(self.Info)
        return ag_new

    def to_json(self, full=False):
        js = dict()
        js['Name'] = self.Name
        js['Info'] = dict(self.Info)
        js['State'] = self.State.Name
        if full:
            js['Trans'] = {tr.Name: tte for tr, tte in self.Trans.items()}
            js['Mods'] = self.Mods.to_json()
        return js
