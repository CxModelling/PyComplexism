from dzdy.mcore import *
from .summarizer import *
from .selector import *
from collections import OrderedDict

__author__ = 'TimeWz667'
__all__ = ['ObsModelSet', 'ModelSet']


class ObsModelSet(Observer):
    def __init__(self):
        Observer.__init__(self)

    def single_observe(self, model, ti):
        self.Last = OrderedDict()
        self.Last['Time'] = ti
        for k, v in model.Summarizer.Summary.items():
            self.Last[k] = v


class ModelSet(BranchModel):
    def __init__(self, name, odt=1):
        BranchModel.__init__(self, name)
        self.Summarizer = Summarizer(dt=odt)
        self.Obs = ObsModelSet()

    def __getitem__(self, item):
        return self.Summarizer.Summary[item]

    def select(self, name):
        return self.Models[name]

    def select_all(self, sel):
        return ModelSelector(self.Models).select_all(sel)

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
            m.impulse_foreign(self, ti)

    def observe(self, ti):
        for m in self.Models.values():
            m.observe(ti)

        self.Obs.observe(self, ti)

    def __deepcopy__(self):
        pass

    def find_next(self):
        for k, model in self.Models.items():
            self.Requests.add([evt.up(k) for evt in model.next])
        su = self.Summarizer.next
        self.Requests.append_src('Summary', su, su.Time)

    def do_request(self, req):
        if req.Node is 'Summary':
            ti = req.Time
            for m in self.Models.values():
                m.observe(ti)
            self.Summarizer.summarise(self.Models, req.Event)
            for m in self.Models.values():
                m.impulse_foreign(self, ti)

    def link(self, src, tar):

        for m in self.Models.values():
            m.listen(self.Name, src_par, tar_par)

    def output(self):
        return self.Obs.observation

    def to_json(self):
        # todo
        pass
