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

    def update_info(self, info, force=False):
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
        self.drop_next()

    def assign(self, evt):
        self.Next = evt

    def exec(self, evt):
        if evt is not Event.NullEvent:
            self.State = self.State.exec(evt.Transition)

    def update(self, ti):
        new_trs = self.State.next_transitions()
        ad = list(set(new_trs) - set(self.Trans.keys()))
        self.Trans = {k: v for k, v in self.Trans.items() if k in new_trs}
        for tr in ad:
            tte = tr.rand()
            for mo in self.Mods.on(tr):
                tte = mo.modify(tte, ti)
            self.Trans[tr] = tte + ti
        self.drop_next()

    def shock(self, m: str, val: float, ti: float):
        mod = self.Mods[m]
        if mod.update(val) and mod.target in self.Trans:
            tr = mod.target
            tte = tr.rand()
            for mo in self.Mods.on(tr):
                tte = mo.modify(tte, ti)
            self.Trans[tr] = tte + ti
            self.drop_next()

    def modify(self, m, ti):
        mod = self.Mods[m]
        if mod.target in self.Trans:
            tr = mod.target
            tte = tr.rand()
            for mo in self.Mods.on(tr):
                tte = mo.modify(tte, ti)
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
        s += ', '.join([str(k) + ': ' + str(v) for k, v in self.Info.items()])
        s += ', State: ' + str(self.State.Value)
        return s

    @property
    def detail(self):
        nxt = self.next
        trs = '\n'.join('\t{}@{}{}'.format(k, v, '*' if k is nxt else '') for k, v in self.Trans.items())
        info = '\n'.join('{}: {}'.format(k, v) for k, v in self.Info.items())
        return 'ID: {}\nState: {}\n{}\n\nTransitions:\n{}'.format(self.Name, self.State, info, trs)
