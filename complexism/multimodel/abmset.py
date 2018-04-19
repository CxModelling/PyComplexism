from complexism.mcore import *
from .summariser import *
from collections import OrderedDict

__author__ = 'TimeWz667'


class ObsABMSet(Observer):
    def __init__(self):
        Observer.__init__(self)

    def single_observe(self, model, ti):
        self.Last = OrderedDict()
        self.Last['Time'] = ti
        for k, v in model.Summarizer.Summary.items():
            self.Last[k] = v


class ABMSet(BranchModel):
    def __init__(self, name, odt=0.5):
        BranchModel.__init__(self, name)
        self.Summarizer = Summarizer(dt=odt)
        self.Relations = list()
        self.Obs = ObsABMSet()

    def __getitem__(self, item):
        return self.Summarizer.Summary[item]

    def append(self, model):
        self.Models[model.Name] = model

    def add_obs_st(self, st):
        for m in self.Models.values():
            m.add_obs_state(st)

    def add_obs_tr(self, tr):
        for m in self.Models.values():
            m.add_obs_tr(tr)

    def add_obs_fun(self, fun):
        for m in self.Models.values():
            m.add_obs_fun(fun)

    def add_obs_be(self, be):
        for m in self.Models.values():
            m.add_obs_be(be)

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

    def set_seed(self, seed=1167):
        for model in self.Models.values():
            model.set_seed(seed)

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

    def link(self, src_par, tar_par):
        self.Relations.append([src_par, tar_par])
        for m in self.Models.values():
            m.listen(self.Name, src_par, tar_par)

    def output(self):
        return self.Obs.observation

    def to_json(self):
        # todo
        pass
