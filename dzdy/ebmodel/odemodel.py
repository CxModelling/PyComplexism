from dzdy import Observer, LeafModel, Clock, Request
from collections import OrderedDict
from scipy.integrate import odeint
import numpy as np
from copy import deepcopy

__author__ = 'TimeWz667'


class ObsODE(Observer):
    def __init__(self):
        Observer.__init__(self)

    def single_observe(self, model, ti):
        self.Last = OrderedDict()
        self.Last["Time"] = ti
        for k, v in zip(model.Y_Names, model.Y):
            self.Last[k] = v


class CoreODE:
    def __init__(self, func, pars):
        self.Func = func
        self.Pars = pars

    def __call__(self, y, t):
        return self.Func(y, t, self.Pars)

    def __setitem__(self, k, v):
        if k in self.Pars:
            self.Pars[k] = v

    def __getitem__(self, k):
        try:
            return self.Pars[k]
        except IndexError:
            return None

    def __contains__(self, item):
        return item in self.Pars


class ODEModel(LeafModel):
    def __init__(self, name, ode, y_names, pars, dt, fdt=None):
        LeafModel.__init__(self, name)
        self.Obs = ObsODE()
        self.Y = None
        self.Y_Names = y_names
        self.DCore = CoreODE(ode, pars)
        self.Clock = Clock(by=dt)
        self.Fdt = fdt if fdt else dt
        self.ForeignLock = dict()
        self.TimeLast = 0

    def observe(self, ti):
        if ti > self.TimeLast:
            self.go_to(ti)
        self.Obs.observe(self, ti)

    def output(self):
        return self.Obs.observation

    def read_y0(self, y0, ti):
        self.Y = [y0[name] if name in y0 else 0 for name in self.Y_Names]

    def reset(self, ti):
        self.Clock.initialise(ti, ti)
        self.TimeLast = ti

    def to_json(self):
        pass

    def go_to(self, ti):
        f, t = self.TimeLast, ti
        self.TimeLast = ti
        num = int((t - f) / self.Fdt) + 1
        ts = np.linspace(f, t, num)
        self.Y = odeint(self.DCore, self.Y, ts)[-1]
        self.Clock.update(ti)

    def do_request(self, req):
        if req.Time > self.TimeLast:
            self.go_to(req.Time)

    def listen(self, mod_src, par_src, t_tar):
        try:
            if t_tar in self.DCore:
                self.ForeignLock[mod_src].append((par_src, t_tar))
        except KeyError:
            if t_tar in self.DCore:
                self.ForeignLock[mod_src] = [(par_src, t_tar)]

    def impulse_foreign(self, fore, ti):
        try:
            imp = self.ForeignLock[fore.Name]
            for f, t in imp:
                self.DCore[t] = fore[f]
        except KeyError:
            return

    def clone(self, pars=None):
        cp = deepcopy(self.DCore.Pars)
        if pars:
            cp.update(pars)
        co = ODEModel(self.Name, deepcopy(self.DCore.Func),
                      self.Y_Names, cp,
                      self.Clock.By, self.Fdt)
        co.Clock.Initial = self.Clock.Initial
        co.Clock.Last = self.Clock.Last
        co.TimeLast = self.TimeLast
        co.ForeignLock = deepcopy(self.ForeignLock)
        co.Obs.TimeSeries = deepcopy(self.Obs.TimeSeries)
        co.Obs.Last = deepcopy(self.Obs.Last)
        co.Y = deepcopy(self.Y)
        return co

    def find_next(self):
        self.Requests.append(Request(None, self.Clock.get_next()))

    def __deepcopy__(self):
        pass
