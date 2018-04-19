from complexism import Observer, BranchModel
from complexism.multimodel import Summariser
from collections import OrderedDict

__author__ = 'TimeWz667'


class ObsLightSet(Observer):
    def __init__(self):
        Observer.__init__(self)

    def single_observe(self, model, ti):
        self.Last = OrderedDict()
        self.Last['Time'] = ti
        for k, v in model.Summariser.Summary.items():
            self.Last[k] = v
        for k, v in model.SystemDynamics.Obs.Last.items():
            if k is not 'Time':
                self.Last['SD.{}'.format(k)] = v


class LightSet(BranchModel):
    def __init__(self, name, sdy, odt=0.5):
        BranchModel.__init__(self, name)
        self.SystemDynamics = sdy
        self.Summarizer = Summariser(dt=odt)
        self.Relations = {'ABM': list(), 'SD': list()}
        self.Obs = ObsLightSet()

    def __getitem__(self, item):
        return self.Summarizer.Summary[item]

    def append(self, model):
        self.Models[model.Name] = model

    def add_obs_state(self, st):
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

    def read_y0(self, y0, ti):
        for k, v in y0.items():
            try:
                self.Models[k].read_y0(y0=v, ti=ti)
            except KeyError:
                self.SystemDynamics.read_y0(y0=v, ti=ti)

    def reset(self, ti):
        for m in self.Models.values():
            m.reset(ti)
            m.observe(ti)
        self.SystemDynamics.reset(ti)
        self.SystemDynamics.observe(ti)
        self.Summarizer.initialise(self.Models, ti)
        for m in self.Models.values():
            m.impulse_foreign(self, ti)
        self.SystemDynamics.impulse_foreign(self, ti)

    def observe(self, ti):
        for m in self.Models.values():
            m.observe(ti)
        self.SystemDynamics.observe(ti)
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
        su = self.SystemDynamics.next[0]
        su.Node = 'SD'
        self.Requests.append(self.SystemDynamics.next[0])

    def do_request(self, req):
        if req.Node is 'Summary':
            ti = req.Time
            for m in self.Models.values():
                m.observe(ti)
            self.SystemDynamics.observe(ti)
            self.Summarizer.summarise(self.Models, req.Event)
            self.SystemDynamics.impulse_foreign(self, ti)
            for m in self.Models.values():
                m.impulse_foreign(self, ti)

        elif req.Node is 'SD':
            self.SystemDynamics.exec()

    def link(self, src_par, tar_par, to='ABM'):
        if to is 'ABM':
            self.Relations['ABM'].append((src_par, tar_par))
            for m in self.Models.values():
                m.listen(self.Name, src_par, tar_par)
        elif to is 'SD':
            self.Relations['SD'].append((src_par, tar_par))
            self.SystemDynamics.listen(self.Name, src_par, tar_par)

    def output(self):
        return self.Obs.observation

    def to_json(self):
        pass

    def clone(self, **kwargs):
        pass
