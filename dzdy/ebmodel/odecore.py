import numpy as np
from collections import namedtuple

__author__ = 'TimeWz667'
__all__ = ['MetaCoreEBM', 'CoreODE']


MetaCoreEBM = namedtuple('MetaEBM', ('PC', 'DC', 'Prototype'))


class Incidence:
    def __init__(self, src, tar, tr):
        self.Src = src
        self.Tar = tar
        self.Transition = tr.Name
        self.Rate = self.__Rate0 = 1 / tr.Dist.mean()

    def reset(self):
        self.Rate = self.__Rate0

    def __repr__(self):
        return '{}({}->{})={}'.format(self.Transition, self.Src, self.Tar, self.Rate)


class CoreODE:
    def __init__(self, dc):
        self.DCore = dc
        self.Y_Names = list(dc.WellDefinedStates)
        self.Y_N = len(self.Y_Names)
        self.Transition_Names = list(dc.Transitions.keys())
        self.Flows = list()
        self.Mods = dict()
        # self.initialise(dc)
        self.Ys = None
        self.FlowLast = list()

    def __getitem__(self, item):
        return self.Mods[item].Value

    def __setitem__(self, item, value):
        self.Mods[item].Value = value

    def initialise(self, model, ti):
        for src in self.Y_Names:
            st_src = self.DCore[src]
            i_src = self.Y_Names.index(st_src.Name)
            for tr in st_src.next_transitions():
                i_tar = self.Y_Names.index(st_src.exec(tr).Name)
                self.Flows.append(Incidence(i_src, i_tar, tr))
        for be in self.Mods.values():
            be.initialise(model, self, ti)

    def update(self, y, ti):
        if self.Mods:
            for flow in self.Flows:
                flow.reset()

            for mod in self.Mods.values():
                for flow in self.Flows:
                    if flow.Transition == mod.Target:
                        flow.Rate = mod.modify(flow.Rate, self, y, ti)

        self.FlowLast = [(flow.Src, flow.Tar, flow.Transition, flow.Rate * y[flow.Src]) for flow in self.Flows]

    def __call__(self, y, t):
        self.update(y, t)

        inflows = self.FlowLast
        outflows = self.FlowLast
        for be in self.Mods.values():
            inflows = be.modify_in(inflows, self, t)
            outflows = be.modify_out(outflows, self, t)

        dy = np.zeros(self.Y_N)
        for i in range(self.Y_N):
            dy[i] += sum([wt for src, tar, tr, wt in inflows if tar is i])
            dy[i] -= sum([wt for src, tar, tr, wt in outflows if src is i])

        return dy

    def add_behaviour(self, be):
        self.Mods[be.Name] = be

    def form_ys(self, y):
        ys = np.zeros(self.Y_N)
        for k, v in enumerate(self.Y_Names):
            if v in y:
                ys[k] = y[v]
        return ys

    def set_Ys(self, ys):
        self.Ys = {k: y for k, y in zip(self.Y_Names, ys) if y != 0}

    def find_states(self, st):
        st = self.DCore[st]
        return [int(self.DCore[y].isa(st)) for y in self.Y_Names]

    def count_st_ys(self, st, ys):
        sel = self.find_states(st)
        return sum([n for s, n in zip(sel, ys) if s])

    def compose_incidence(self, src, tar, tr, rate):
        si = self.Y_Names.index(src) if src else -1
        ti = self.Y_Names.index(tar) if tar else -1
        return si, ti, tr, rate

    def count_st(self, st):
        st = self.DCore[st]
        return sum([n for y, n in self.Ys.items() if self.DCore[y].isa(st)])

    def count_tr(self, tr):
        return sum([wt for _, _, t, wt in self.FlowLast if t == tr])

    def fill(self, be, rec, ti):
        self.Mods[be].fill(rec, self, ti)

    def clone(self, **kwargs):
        dc = kwargs['dc'] if 'dc' in kwargs else self.DCore
        core = CoreODE(dc)
        core.FlowLast = list(self.FlowLast)
        core.Ys = dict(self.Ys.items())
        return core

    def to_json(self):
        pass
