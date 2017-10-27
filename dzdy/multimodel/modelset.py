from dzdy.mcore import *
from .summariser import *
from collections import OrderedDict
from dzdy.multimodel import RelationEntry

__author__ = 'TimeWz667'
__all__ = ['ObsModelSet', 'ModelSet']


class ObsModelSet(Observer):
    def __init__(self):
        Observer.__init__(self)
        self.ObsModels = dict()
        self.FullObs = set()
        self.All = False

    def initialise_observation(self, model, ti):
        for m in model.Models.values():
            m.initialise_observation(ti)
        model.Summariser.read_obs(model)
        model.cross_impulse(ti)
        self.update_observation(model, ti)

    def update_observation(self, model, ti):
        for m in model.Models.values():
            m.update_observation(ti)
        model.Summariser.read_obs(model)
        self.Current.update(model.Summariser.Summary)

    def add_obs_model(self, mod):
        self.FullObs.add(mod)

    @property
    def observation(self):
        ts = [OrderedDict(v) for v in self.TimeSeries]
        for m in self.FullObs:
            ob = self.ObsModels[m]
            for a, b in zip(ts, ob.TimeSeries):
                for k, v in b.items():
                    if k != 'Time':
                        a['{}@{}'.format(m, k)] = v

        if self.All:
            obs = [ob.TimeSeries for ob in self.ObsModels.values()]
            obs = [OrderedDict(pd.DataFrame(list(k)).sum()) for k in zip(*obs)]

            for a, b in zip(ts, obs):
                for k, v in b.items():
                    if k != 'Time':
                        a[k] = v

        dat = pd.DataFrame(ts)
        dat = dat.set_index('Time')
        return dat


class ModelSet(BranchModel):
    def __init__(self, name, odt=0.5):
        BranchModel.__init__(self, name, ObsModelSet())
        self.Network = dict()
        self.Network[name] = set()
        self.Summariser = Summariser(name, dt=odt)

    def __getitem__(self, item):
        return self.Obs[item]

    def add_obs_model(self, mod):
        if mod in self.Models:
            self.Obs.add_obs_model(mod)
        elif mod == '*':
            self.Obs.All = True

    def append(self, model):
        self.Models[model.Name] = model
        self.Obs.ObsModels[model.Name] = model.Obs

    def read_y0(self, y0, ti):
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
        self.Requests.append_src('Summary', '', self.Summariser.Requests.Time)

    def do_request(self, req):
        if req.Node == 'Summary':
            ti = req.Time
            self.update_observation(ti)
            self.cross_impulse(ti)
            self.update_observation(ti)
            self.Summariser.Requests.clear()
            self.Summariser.do_request(req)

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

    def push_observation(self, ti):
        for m in self.Models.values():
            m.push_observation(ti)
        BranchModel.push_observation(self, ti)

    def to_json(self):
        # todo
        pass

    def clone(self, **kwargs):
        pass
