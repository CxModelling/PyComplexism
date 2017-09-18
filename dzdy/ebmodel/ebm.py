from dzdy.mcore import Observer, LeafModel, Clock, Request
from collections import OrderedDict
from scipy.integrate import odeint
import numpy as np
from copy import deepcopy
from collections import namedtuple


__author__ = 'TimeWz667'
__all__ = ['ObsEBM', 'ODEModel']


Links = namedtuple('Links', ('mod_src', 'par_src', 'tar', 'par_tar'))


class ObsEBM(Observer):
    def __init__(self):
        Observer.__init__(self)
        self.ObsSt = list()
        self.ObsTr = list()
        self.ObsBe = list()

    def add_obs_state(self, st):
        self.ObsSt.append(st)

    def add_obs_transition(self, tr):
        self.ObsTr.append(tr)

    def add_obs_behaviour(self, be):
        self.ObsBe.append(be)

    def single_observe(self, model, ti):
        self.Last = OrderedDict()
        self.Last['Time'] = ti

        for st in self.ObsSt:
            self.Last['P_{}'.format(st)] = model.ODE.count_st(st)

        for tr in self.ObsTr:
            self.Last['I_{}'.format(tr)] = model.ODE.count_tr(tr)
        for be in self.ObsBe:
            model.ODE.fill(be, self.Last, ti)


class ODEModel(LeafModel):
    def __init__(self, name, core, pc=None, meta=None, dt=1, fdt=None):
        LeafModel.__init__(self, name, meta=meta)
        self.Obs = ObsEBM()
        self.Y = None
        self.PCore = pc
        self.ODE = core
        self.Clock = Clock(by=dt)
        self.ForeignLinks = list()
        self.Fdt = min(dt, fdt) if fdt else dt
        self.TimeLast = 0

    def add_obs_state(self, st):
        self.Obs.add_obs_state(st)

    def add_obs_transition(self, tr):
        self.Obs.add_obs_transition(tr)

    def add_obs_behaviour(self, be):
        self.Obs.add_obs_behaviour(be)

    def observe(self, ti):
        if ti > self.TimeLast:
            self.go_to(ti)
        self.Obs.observe(self, ti)

    def __getitem__(self, item):
        return self.Obs.Last[item]

    def output(self):
        return self.Obs.observation

    def read_y0(self, y0, ti):
        self.Y = self.ODE.form_ys(y0)
        self.ODE.set_Ys(self.Y)

    def reset(self, ti):
        self.Clock.initialise(ti, ti)
        self.ODE.update(self.Y, ti)
        self.TimeLast = ti
        self.ODE.initialise(self, ti)
        self.Obs.single_observe(self, ti)

    def to_json(self):
        pass

    def go_to(self, ti):
        f, t = self.TimeLast, ti
        self.TimeLast = ti
        num = int((t - f) / self.Fdt) + 1
        ts = np.linspace(f, t, num)
        self.Y = odeint(self.ODE, self.Y, ts)[-1]
        self.ODE.set_Ys(self.Y)
        self.Clock.update(ti)

    def do_request(self, req):
        if req.Time > self.TimeLast:
            self.go_to(req.Time)

    def listen(self, mod_src, par_src, tar, par_tar=None):
        tar = (tar, par_tar) if par_tar else tar
        self.ForeignLinks.append(Links(mod_src, par_src, tar, par_tar))

    def listen_multi(self, mod_src_all, par_src, tar, par_tar=None):
        tar = (tar, par_tar) if par_tar else tar
        self.ForeignLinks.append(Links(mod_src_all, par_src, tar, par_tar))

    def impulse_foreign(self, fore, ti):
        lks = [fl for fl in self.ForeignLinks if fl.mod_src == fore.Name]
        for _, par, tar, par_tar in lks:
            val = fore[par]
            if par_tar is None:
                self.ODE[tar] = val
            else:
                self.ODE[tar, par_tar] = val
        # todo

    def clone(self, **kwargs):
        core = self.ODE.clone(**kwargs)
        pc = kwargs['pc'] if 'pc' in kwargs else None
        co = ODEModel(self.Name, core, pc, self.Meta, dt=self.Clock.By, fdt=self.Fdt)
        co.Clock.Initial = self.Clock.Initial
        co.Clock.Last = self.Clock.Last
        co.TimeLast = self.TimeLast
        co.TimeEnd = self.TimeEnd
        co.Obs.TimeSeries = deepcopy(self.Obs.TimeSeries)
        co.Obs.Last = dict(self.Obs.Last.items())
        co.Y = deepcopy(self.Y)
        core.initialise(co, self.TimeLast)
        return co

    def find_next(self):
        self.Requests.append(Request(None, self.Clock.get_next()))
