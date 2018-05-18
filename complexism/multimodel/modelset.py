import pandas as pd
import networkx as nx
from complexism.misc.counter import count
from complexism.element import Event
from complexism.mcore import *
from .entries import RelationEntry
from .summariser import *


__author__ = 'TimeWz667'
__all__ = ['ObsModelSet', 'MultiModel']


class ObsModelSet(Observer):
    def __init__(self):
        Observer.__init__(self)
        self.Observed = list()

    def add_observing_selector(self, sel):
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


class ObsMultiModel(Observer):
    def __init__(self):
        Observer.__init__(self)
        self.ObservingModels = list()

    def add_observing_model(self, model):
        if model not in self.ObservingModels:
            self.ObservingModels.append(model)

    def update_dynamic_observations(self, model, flow, ti):
        for m in self.ObservingModels:
            mod = model.get_model(m)
            flow.update({'{}@{}'.format(m, k): v for k, v in mod.Obs.Flow.items() if k != 'Time'})

    def read_statics(self, model, tab, ti):
        for m in self.ObservingModels:
            mod = model.get_model(m)
            if tab is self.Last:
                tab.update({'{}@{}'.format(m, k): v for k, v in mod.Obs.Last.items() if k != 'Time'})
            elif self.ExtMid:
                tab.update({'{}@{}'.format(m, k): v for k, v in mod.Obs.Mid.items() if k != 'Time'})


class MultiModel(BranchModel):
    def __init__(self, name, pc=None):
        BranchModel.__init__(self, name, pc, ObsMultiModel())
        self.Models = nx.MultiDiGraph()

    def add_observing_model(self, m):
        if m in self.Models:
            self.Obs.add_observing_model(m)

    def append(self, m):
        if m.Name not in self.Models:
            self.Models.add_node(m.Name, model=m)

    def link(self, src, tar, **kwargs):
        src = src if isinstance(src, RelationEntry) else RelationEntry(src)
        tar = tar if isinstance(tar, RelationEntry) else RelationEntry(tar)

        m_src = self.select_all(src.Selector)
        m_tar = self.select_all(tar.Selector)

        if src.is_single():
            ms = m_src.first()
            for kt, mt in m_tar.items():
                if ms is not mt:
                    mt.listen(ms.Name, src.Parameter, tar.Parameter, **kwargs)
                    self.Models.add_edge(ms.Name, mt.Name, par_src=src.Parameter, par_tar=tar.Parameter)

    def read_y0(self, y0, ti):
        if not y0:
            return
        for k, m in self.Models.nodes().data('model'):
            m.read_y0(y0=y0[k], ti=ti)

    def reset_impulse(self, ti):
        for s, nbd in self.Models.adjacency():
            src = self.get_model(s)
            for t in nbd.keys():
                tar = self.get_model(t)
                tar.impulse_foreign(src, ti)

    @count()
    def do_request(self, req):
        src = self.get_model(req.Who)
        for t, kb in self.Models[req.Who].items():
            # for _, atr in kb.items():
            tar = self.get_model(t)
            tar.impulse_foreign(src, req.When)

    def find_next(self):
        for k, model in self.all_models().items():
            for req in model.Next:
                self.Requests.append_request(req.up_scale(self.Name))
                self.Requests.append_event(req.Event, k, self.Name)
#            self.Requests.append_requests([req.up_scale(k) for req in model.Next])

    def all_models(self):
        return dict(self.Models.nodes().data('model'))

    def get_model(self, k):
        return self.Models.nodes[k]['model']

    def clone(self, **kwargs):
        pass


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

    def add_observing_selector(self, mod):
        self.Obs.add_observing_selector(mod)

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
            self.Requests.append_requests([req.up_scale(k) for req in model.Next])
        self.Summariser.find_next()
        self.Requests.append_event(Event('Summarise', self.Summariser.TTE), 'Summariser', self.Name)

    def do_request(self, req):
        if req.Node == 'Summariser':
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

    def to_json(self):
        # todo
        pass

    def clone(self, **kwargs):
        pass
