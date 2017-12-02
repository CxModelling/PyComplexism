from dzdy.mcore import Observer, LeafModel, Clock, Request
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

    def update_dynamic_Observations(self, model, flow, ti):
        for tr in self.ObsTr:
            flow[tr] = model.ODE.count_tr(tr)

    def read_statics(self, model, tab, ti):
        for st in self.ObsSt:
            tab[st] = model.ODE.count_st(st)
        for be in self.ObsBe:
            model.ODE.fill(be, tab, ti)


class ODEModel(LeafModel):
    def __init__(self, name, core, pc=None, meta=None, dt=1, fdt=None):
        LeafModel.__init__(self, name, ObsEBM(), meta=meta)
        self.Y = None
        self.PCore = pc
        self.ODE = core
        self.UpdateEnd = 0
        self.Clock = Clock(dt=dt)
        self.ForeignLinks = list()
        self.Fdt = min(dt, fdt) if fdt else dt

    def add_obs_state(self, st):
        self.Obs.add_obs_state(st)

    def add_obs_transition(self, tr):
        self.Obs.add_obs_transition(tr)

    def add_obs_behaviour(self, be):
        self.Obs.add_obs_behaviour(be)

    def read_y0(self, y0, ti):
        self.ODE.initialise(self, y0, ti)
        #self.Y = self.ODE.form_ys(self.ODE.Ys)

    def reset(self, ti):
        self.Clock.initialise(ti)
        self.UpdateEnd = self.TimeEnd = ti
        self.ODE.update(self.Y, ti)

    def go_to(self, ti):
        f, t = self.UpdateEnd, ti
        self.UpdateEnd = ti
        num = int((t - f) / self.Fdt) + 1
        ts = np.linspace(f, t, num)
        self.Y = odeint(self.ODE, self.Y, ts)[-1]
        self.ODE.set_Ys(self.Y)
        self.Clock.update(ti)

    def do_request(self, req):
        if req.Time > self.TimeEnd:
            self.go_to(req.Time)

    def find_next(self):
        self.Requests.append(Request(None, self.Clock.Next))

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

    def to_json(self):
        pass

    def clone(self, **kwargs):
        core = self.ODE.clone(**kwargs)
        pc = kwargs['pc'] if 'pc' in kwargs else None
        co = ODEModel(self.Name, core, pc, self.Meta, dt=self.Clock.By, fdt=self.Fdt)
        co.Clock.Initial = self.Clock.Initial
        co.Clock.Last = self.Clock.Last
        co.TimeEnd = self.TimeEnd
        co.UpdateEnd = self.UpdateEnd
        co.Obs.TimeSeries = deepcopy(self.Obs.TimeSeries)
        co.Obs.Last = dict(self.Obs.Last.items())
        co.Y = deepcopy(self.Y)
        core.initialise(co, self.TimeEnd)
        return co
