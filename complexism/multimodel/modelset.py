from complexism.element import Event
from complexism.mcore import *
from .entries import RelationEntry
from .summariser import *

import pandas as pd

__author__ = 'TimeWz667'
__all__ = ['ObsModelSet', 'ModelSet']


class ObsModelSet(Observer):
    def __init__(self):
        Observer.__init__(self)
        self.Observed = list()

    def add_obs_sel(self, sel):
        self.Observed.append(sel)

    def update_dynamic_observations(self, model, flow, ti):
        pass

    def read_statics(self, model, tab, ti):
        s = model.Summariser
        try:
            tab.update(s.Impulses)
            if tab is self.Last:
                for sel in self.Observed:
                    sub = [m.Obs.Last for m in model.select_all(sel).values()]
                    self.fill_table(sel, tab, sub)
            elif self.ExtMid:
                for sel in self.Observed:
                    sub = [m.Obs.Mid for m in model.select_all(sel).values()]
                    self.fill_table(sel, tab, sub)

        except AttributeError:
            return

    @staticmethod
    def fill_table(sel, tab, sub):
        dat = pd.DataFrame(sub)
        tab.update({"{}@{}".format(sel, k): v for k, v in dat.sum().items() if k != 'Time'})


class ModelSet(BranchModel):
    def __init__(self, name, pc=None, odt=0.5):
        BranchModel.__init__(self, name, ObsModelSet())
        self.PCore = pc
        self.Network = dict()
        self.Network[name] = set()
        self.Summariser = Summariser(name, dt=odt)
        self.Summariser.Employer = self

    def __getitem__(self, item):
        return self.Obs[item]

    def add_obs_model(self, mod):
        self.Obs.add_obs_sel(mod)

    def append(self, model):
        self.Models[model.Name] = model

    def read_y0(self, y0, ti):
        if not y0:
            return
        for k, v in y0.items():
            self.Models[k].read_y0(y0=v, ti=ti)

    def reset(self, ti):
        for m in self.Models.values():
            m.reset(ti)
        self.Summariser.reset(ti)

    def find_next(self):
        for k, model in self.Models.items():
            self.Requests.add([evt.up(k) for evt in model.next])
        self.Summariser.find_next()
        self.Requests.append_event(Event('Summarise', self.Summariser.TTE), 'Summariser', self.Name)

    def do_request(self, req):
        if req.Node == 'Summarise':
            ti = req.Time
            self.cross_impulse(ti)
            self.Summariser.do_request(req)
            self.Summariser.drop_next()

    def link(self, src, tar):
        src = src if isinstance(src, RelationEntry) else RelationEntry(src)
        tar = tar if isinstance(tar, RelationEntry) else RelationEntry(tar)

        if src.Selector == self.Name:
            m_tar = self.select_all(tar.Selector)
            for kt, mt in m_tar.items():
                mt.listen(src.Selector, src.Parameter, tar.Parameter)
                try:
                    self.Network[self.Name].add(kt)
                except KeyError:
                    self.Network[self.Name] = {kt}
            return

        if tar.Selector == self.Name:
            m_src = self.select_all(src.Selector)
            self.Summariser.listen(src.Selector, src.Parameter, tar.Parameter)
            for m in m_src.keys():
                try:
                    self.Network[m].add(self.Name)
                except KeyError:
                    self.Network[m] = {self.Name}
            return

        m_src = self.select_all(src.Selector)
        m_tar = self.select_all(tar.Selector)

        if src.is_single():
            ms = m_src.first()
            for kt, mt in m_tar.items():
                if ms is not mt:
                    mt.listen(ms.Name, src.Parameter, tar.Parameter)
                    try:
                        self.Network[ms.Name].add(kt)
                    except KeyError:
                        self.Network[ms.Name] = {kt}
        else:
            for mt in m_tar.values():
                ms = [m for m in m_src.keys() if m == mt.Name]
                mt.listen_multi(ms, src.Parameter, tar.Parameter)
                for m in m_src:
                    try:
                        self.Network[m].add(mt)
                    except KeyError:
                        self.Network[m] = {mt}

    def cross_impulse(self, ti):
        for k, vs in self.Network.items():
            ms = self.Summariser if k is self.Name else self.Models[k]
            for v in vs:
                if v is self.Name:
                    continue
                mt = self.Models[v]
                mt.impulse_foreign(ms, ti)

    def initialise_observations(self, ti):
        for m in self.Models.values():
            m.initialise_observations(ti)
        BranchModel.initialise_observations(self, ti)

    def update_observations(self, ti):
        for m in self.Models.values():
            m.update_observations(ti)
        BranchModel.update_observations(self, ti)

    def captureMidTermObservations(self, ti):
        for m in self.Models.values():
            m.captureMidTermObservations(ti)
        BranchModel.captureMidTermObservations(self, ti)

    def push_observations(self, ti):
        for m in self.Models.values():
            m.push_observations(ti)
        BranchModel.push_observations(self, ti)

    def to_json(self):
        # todo
        pass

    def clone(self, **kwargs):
        pass
