from dzdy.mcore import *
from .summariser import *
from collections import OrderedDict

__author__ = 'TimeWz667'
__all__ = ['ObsModelSet', 'ModelSet']


class ObsModelSet(Observer):
    def __init__(self):
        Observer.__init__(self)

    def point_observe(self, model, ti):
        self.Last = OrderedDict()
        self.Last['Time'] = ti
        self.after_shock_observe(model, ti)

    def after_shock_observe(self, model, ti):
        model.Summariser.read_obs(model)
        for k, v in model.Summariser.Summary.items():
            self.Last[k] = v


class ModelSet(BranchModel):
    def __init__(self, name, odt=1):
        BranchModel.__init__(self, name, ObsModelSet())
        self.Network = dict()
        self.Network[name] = set()
        self.Summariser = Summariser(dt=odt)

    def __getitem__(self, item):
        return self.Obs[item]

    def append(self, model):
        self.Models[model.Name] = model

    def read_y0(self, y0, ti):
        for k, v in y0.items():
            self.Models[k].read_y0(y0=v, ti=ti)

    def reset(self, ti):
        for m in self.Models.values():
            m.reset(ti)
            m.observe(ti)
        self.Summariser.reset(ti)
        self.Summariser.read_obs(self)
        for k, vs in self.Network.items():
            ms = self.Summariser if k is self.Name else self.Models[k]
            for v in vs:
                if v is self.Name:
                    continue
                mt = self.Models[v]
                mt.impulse_foreign(ms, ti)
        self.Obs.point_observe(self, ti)



        self.after_shock_observe(ti)

    def observe(self, ti):
        for m in self.Models.values():
            m.observe(ti)
        self.Obs.observe(self, ti)
        for k, vs in self.Network.items():
            ms = self.Summariser if k is self.Name else self.Models[k]
            for v in vs:
                if v is self.Name:
                    continue
                mt = self.Models[v]
                mt.impulse_foreign(ms, ti)
        self.after_shock_observe(ti)

    def after_shock_observe(self, ti):
        for m in self.Models.values():
            m.after_shock_observe(ti)
        self.Obs.after_shock_observe(self, ti)

    def find_next(self):
        for k, model in self.Models.items():
            self.Requests.add([evt.up(k) for evt in model.next])
        self.Summariser.find_next()
        self.Requests.append_src('Summary', '', self.Summariser.Requests.Time)

    def do_request(self, req):
        if req.Node == 'Summary':
            ti = req.Time
            self.after_shock_observe(ti)
            for k, vs in self.Network.items():
                ms = self.Summariser if k is self.Name else self.Models[k]
                for v in vs:
                    if v is self.Name:
                        continue
                    mt = self.Models[v]
                    mt.impulse_foreign(ms, ti)
            self.after_shock_observe(ti)
            self.Summariser.Requests.clear()
            self.Summariser.do_request(req)

    def link(self, src, tar):
        if src.Selector == self.Name:
            m_tar = self.select_all(tar.Selector)
            for m in m_tar:
                m.listen(src.Selector, src.Parameter, tar.Parameter)
                try:
                    self.Network[self.Name].add(m.Name)
                except KeyError:
                    self.Network[self.Name] = {m.Name}
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
            for mt in m_tar.keys():
                if ms is not mt:
                    mt.listen(ms.Name, src.Parameter, tar.Parameter)
                    try:
                        self.Network[ms].add(mt)
                    except KeyError:
                        self.Network[ms] = {mt}
        else:
            for mt in m_tar.keys():
                for ms in m_src:
                    if ms is not mt:
                        mt.listen_multi(ms.Name, src.Parameter, tar.Parameter)
                        try:
                            self.Network[ms].add(mt)
                        except KeyError:
                            self.Network[ms] = {mt}

    def to_json(self):
        # todo
        pass

    def clone(self, **kwargs):
        pass
