from dzdy.dcore import Event
from dzdy.mcore import *


__author__ = 'TimeWz667'
__all__ = ['ObsDualModel', 'DualModel']


class ObsDualModel(Observer):
    def __init__(self):
        Observer.__init__(self)

    def initialise_observation(self, model, ti):
        for m in model.Models.values():
            m.initialise_observation(ti)
        self.read(model.Models)
        model.cross_impulse(ti)
        self.update_observation(model, ti)

    def update_observation(self, model, ti):
        for m in model.Models.values():
            m.update_observation(ti)
        self.read(model.Models)

    def read(self, ms):
        for mn, mod in ms.items():
            for k, v in mod.Obs.Current.items():
                self.Current['{}:{}'.format(mn, k)] = v


class DualModel(BranchModel):
    def __init__(self, name, odt=0.5):
        BranchModel.__init__(self, name, ObsDualModel())
        self.ObsDT = Clock(odt)
        self.NameA = None
        self.NameZ = None

    def __getitem__(self, item):
        return self.Obs[item]

    def append(self, model):
        if len(self.Models) < 2:
            self.Models[model.Name] = model
            if not self.NameA:
                self.NameA = model.Name
            elif not self.NameZ:
                self.NameZ = model.Name

    def read_y0(self, y0, ti):
        for k, v in y0.items():
            self.Models[k].read_y0(y0=v, ti=ti)

    def reset(self, ti):
        for m in self.Models.values():
            m.reset(ti)
        self.ObsDT.initialise(ti, ti)

    def find_next(self):
        for k, model in self.Models.items():
            self.Requests.add([evt.up(k) for evt in model.next])
        su = Event('Summary', self.ObsDT.get_next())
        self.Requests.append_src('Summary', su, su.Time)

    def do_request(self, req):
        if req.Node == 'Summary':
            ti = req.Time
            self.ObsDT.update(ti)
            self.update_observation(ti)
            self.cross_impulse(ti)
            self.update_observation(ti)

    def link(self, src, tar):
        if src.is_single():
            self.Models[tar.Selector].listen(src.Selector, src.Parameter, tar.Parameter)

    def cross_impulse(self, ti):
        self.Models[self.NameA].impulse_foreign(self.Models[self.NameZ], ti)
        self.Models[self.NameZ].impulse_foreign(self.Models[self.NameA], ti)

    def push_observation(self, ti):
        for m in self.Models.values():
            m.push_observation(ti)
        BranchModel.push_observation(self, ti)

    def to_json(self):
        # todo
        pass

    def clone(self, **kwargs):
        pass
