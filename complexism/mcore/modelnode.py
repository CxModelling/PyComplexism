from complexism.mcore import *
from abc import ABCMeta, abstractmethod

__author__ = 'TimeWz667'


__all__ = ['LeafModel', 'BranchModel']


class AbsModel(metaclass=ABCMeta):
    def __init__(self, name, obs: Observer, meta=None):
        self.Meta = meta
        self.Name = name
        self.Obs = obs
        self.Requests = RequestSet()
        self.TimeEnd = None

    def initialise(self, ti=None, y0=None):
        if y0:
            self.read_y0(y0, ti)
        self.reset(ti)
        self.drop_next()

    def reset(self, ti):
        pass

    def __getitem__(self, item):
        return self.Obs[item]

    def output(self, mid=False):
        if mid:
            return self.Obs.AdjustedObservations
        else:
            return self.Obs.Observations

    def read_y0(self, y0, ti):
        pass

    def listen(self, src_model, src_value, par_target):
        pass

    @property
    def next(self):
        if self.Requests.is_empty():
            self.find_next()
        return self.Requests.Requests

    @property
    def tte(self):
        return self.Requests.Time

    def drop_next(self):
        self.Requests.clear()

    @abstractmethod
    def find_next(self):
        pass

    @abstractmethod
    def fetch(self, rs):
        pass

    @abstractmethod
    def exec(self):
        pass

    @abstractmethod
    def do_request(self, req):
        pass

    def initialise_observations(self, ti):
        self.Obs.initialise_observations(self, ti)

    def update_observations(self, ti):
        self.Obs.observe_routinely(self, ti)

    def captureMidTermObservations(self, ti):
        self.Obs.update_at_mid_term(self, ti)

    def push_observations(self, ti):
        self.Obs.push_observations(ti)

    @abstractmethod
    def clone(self, **kwargs):
        pass


class LeafModel(AbsModel, metaclass=ABCMeta):
    def __init__(self, name, obs, meta=None):
        AbsModel.__init__(self, name, obs, meta)

    def fetch(self, rs):
        self.Requests.clear()
        self.Requests.add(rs)

    def exec(self):
        for req in self.Requests:
            self.do_request(req)
        self.drop_next()


class BranchModel(AbsModel, metaclass=ABCMeta):
    def __init__(self, name, obs, meta=None):
        AbsModel.__init__(self, name, obs, meta)
        self.Models = dict()

    def select(self, mod):
        return self.Models[mod]

    def select_all(self, sel):
        return ModelSelector(self.Models).select_all(sel)

    def fetch(self, res):
        self.Requests.clear()
        self.Requests.add(res)
        self.pass_down()

    def pass_down(self):
        res = self.Requests.pop_lower_requests()
        nest = dict()
        for req in res:
            m, req = req.down()
            try:
                nest[m].append(req)
            except KeyError:
                nest[m] = [req]

        for k, v in nest.items():
            self.select(k).fetch(v)

    def exec(self):
        for req in self.Requests:
            self.do_request(req)

        for v in self.Models.values():
            if v.tte == self.tte:
                v.exec()
        self.drop_next()

    @abstractmethod
    def do_request(self, req):
        pass
