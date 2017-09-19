from dzdy.mcore import *
from dzdy.dcore import Event
from .selector import *
from collections import OrderedDict

__author__ = 'TimeWz667'
__all__ = ['ObsDualModel', 'DualModel']


class ObsDualModel(Observer):
    def __init__(self):
        Observer.__init__(self)

    def single_observe(self, model, ti):
        self.Last = OrderedDict()
        self.Last['Time'] = ti
        for mn, mod in model.Models.items():
            for k, v in mod.Obs.Last.items():
                if k is not 'Time':
                    self.Last['{}:{}'.format(mn, k)] = v


class DualModel(BranchModel):
    def __init__(self, name, odt=1):
        BranchModel.__init__(self, name)
        self.Obs = ObsDualModel()
        self.ObsDT = Clock(odt)
        self.NameA = None
        self.NameZ = None

    def __getitem__(self, item):
        return self.Obs[item]

    def select(self, name):
        return self.Models[name]

    def select_all(self, sel):
        return ModelSelector(self.Models).select_all(sel)

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
        self.ObsDT.initialise(ti)
        for m in self.Models.values():
            m.reset(ti)
            m.observe(ti)

        self.Obs.single_observe(self, ti)
        self.Models[self.NameA].impulse_foreign(self.Models[self.NameZ], ti)
        self.Models[self.NameZ].impulse_foreign(self.Models[self.NameA], ti)

    def observe(self, ti):
        for m in self.Models.values():
            m.observe(ti)
        self.Obs.observe(self, ti)

    def find_next(self):
        for k, model in self.Models.items():
            self.Requests.add([evt.up(k) for evt in model.next])

        su = Event('Summary', self.ObsDT.get_next())
        self.Requests.append_src('Summary', su, su.Time)

    def do_request(self, req):
        if req.Node == 'Summary':
            ti = req.Time
            self.ObsDT.update(ti)
            for m in self.Models.values():
                m.observe(ti)
            self.Obs.single_observe(self, ti)

            self.Models[self.NameA].impulse_foreign(self.Models[self.NameZ], ti)
            self.Models[self.NameZ].impulse_foreign(self.Models[self.NameA], ti)

            for m in self.Models.values():
                m.observe(ti)
            self.Obs.single_observe(self, ti)

    def link(self, src, tar):
        if src.is_single():
            self.Models[tar.Selector].listen(src.Selector, src.Parameter, tar.Parameter)

    def output(self):
        return self.Obs.observation

    def to_json(self):
        # todo
        pass

    def clone(self, **kwargs):
        pass
