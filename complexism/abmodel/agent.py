from complexism.mcore import ModelAtom
from complexism.element import Event
from abc import abstractmethod, ABCMeta

__author__ = 'TimeWz667'


class GenericAgent(ModelAtom, metaclass=ABCMeta):
    def __init__(self, name, pars=None):
        ModelAtom.__init__(self, name, pars)

    def find_next(self):
        if self.Trans:
            return Event(*min(self.Trans.items(), key=lambda x: x[1]))
        else:
            return Event.NullEvent

    def initialise(self, ti):
        self.Trans.clear()
        self.update(ti)

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
