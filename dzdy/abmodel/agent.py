from dzdy.dcore import Event
from dzdy.abmodel import ModifierSet

__author__ = 'TimeWz667'


class Agent:
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
