from dzdy.mcore import *
from .summarizer import *

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
        model.Summarizer.read_obs(model.Models)
        model.Summarizer.reform_summary()
        for k, v in model.Summarizer.Summary.items():
            self.Last[k] = v


class ModelSet(BranchModel):
    def __init__(self, name, odt=1):
        BranchModel.__init__(self, name, ObsModelSet())
        self.Network = dict()
        self.Summarizer = Summarizer(dt=odt)

    def __getitem__(self, item):
        return self.Obs[item]

    def append(self, model):
        self.Models[model.Name] = model

    def add_summary(self, su):
        self.Summarizer.Func.append(su)

    def read_y0(self, y0, ti):
        for k, v in y0.items():
            self.Models[k].read_y0(y0=v, ti=ti)

    def reset(self, ti):
        for m in self.Models.values():
            m.reset(ti)
            m.observe(ti)

        self.Summarizer.initialise(self.Models, ti)
        for m in self.Models.values():
            for fore in self.Models.values():
                if m is not fore:
                    m.impulse_foreign(fore, ti)
        self.Obs.point_observe(self, ti)

    def observe(self, ti):
        for m in self.Models.values():
            m.observe(ti)
        self.Obs.observe(self, ti)

    def after_shock_observe(self, ti):
        for m in self.Models.values():
            m.after_shock_observe(ti)
        self.Obs.after_shock_observe(ti)

    def find_next(self):
        for k, model in self.Models.items():
            self.Requests.add([evt.up(k) for evt in model.next])
        su = self.Summarizer.next
        self.Requests.append_src('Summary', su, su.Time)

    def do_request(self, req):
        if req.Node is 'Summary':
            ti = req.Time
            self.observe(ti)
            for m in self.Models.values():
                m.impulse_foreign(self, ti)
            self.after_shock_observe(ti)

    def link(self, src, tar):
        if src.is_single():
            for m in self.select_all(tar.Selector):
                m.listen(src.Selector, src.Parameter, tar.Parameter)

        else:
            ss = self.select_all(src.Selector)
            ss = [sr.Name for sr in ss]
            for m in self.select_all(tar.Selector):
                m.listen_multi(ss, src.Parameter, tar.Parameter)

    def to_json(self):
        # todo
        pass

    def clone(self, **kwargs):
        pass
