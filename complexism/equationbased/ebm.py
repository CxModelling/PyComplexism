import numpy as np
from copy import deepcopy
from collections import namedtuple
from scipy.integrate import odeint
from abc import ABCMeta, abstractmethod
from complexism.mcore import Observer, LeafModel
from complexism.element import Clock, Request, Event


__author__ = 'TimeWz667'
__all__ = ['AbsEquations', 'OrdinaryDifferentialEquations',
           'ObsEBM', 'GenericEquationBasedModel']


Links = namedtuple('Links', ('mod_src', 'par_src', 'par_tar', 'kwargs'))


class AbsEquations(metaclass=ABCMeta):
    @abstractmethod
    def set_y(self, y):
        pass

    @abstractmethod
    def get_y_dict(self):
        pass

    @abstractmethod
    def update(self, t0, t1, pars):
        pass

    @abstractmethod
    def impulse(self, k, v):
        pass


class OrdinaryDifferentialEquations(AbsEquations):
    def __init__(self, fn, y_names, dt, x=None):
        self.Dt = dt
        self.Y = np.zeros(len(y_names))
        self.X = x if x else dict()
        self.NamesY = y_names
        self.IndicesY = {v: i for i, v in enumerate(y_names)}
        self.Func = fn

    def __getitem__(self, item):
        return self.X[item]

    def set_y(self, y):
        n = len(self.NamesY)
        if len(y) is not n:
            raise AttributeError

        if isinstance(y, list):
            self.Y = np.array(y)
        else:
            self.Y = np.zeros(n)
            for k, i in self.IndicesY.items():
                self.Y[i] = y[k]

    def get_y_dict(self):
        return {v: self.Y[i] for v, i in self.IndicesY.items()}

    def update(self, t0, t1, pars):
        num = int((t1 - t0) / self.Dt) + 1
        ts = np.linspace(t0, t1, num)
        self.Y = odeint(self.Func, self.Y, ts, args=(pars, self.X))[-1]
        return self.get_y_dict()

    def impulse(self, k, v):
        self.X[k] = v


class ObsEBM(Observer):
    def __init__(self):
        Observer.__init__(self)
        self.Stocks = list()
        self.StockFunctions = list()
        self.FlowFunctions = list()

    def add_observing_stock(self, stock):
        self.Stocks.append(stock)

    def add_observing_stock_function(self, func):
        self.StockFunctions.append(func)

    def add_observing_flow_function(self, func):
        self.FlowFunctions.append(func)

    def update_dynamic_observations(self, model, flow, ti):
        model.go_to(ti)
        for func in self.FlowFunctions:
            func(model, flow, ti)

    def read_statics(self, model, tab, ti):
        model.go_to(ti)
        for st in self.Stocks:
            tab[st] = model.Y[st]

        for func in self.StockFunctions:
            func(model, tab, ti)


class GenericEquationBasedModel(LeafModel):
    def __init__(self, name, pc, eqs, dt, obs=None):
        obs = obs if obs else ObsEBM()
        LeafModel.__init__(self, name, obs)
        self.PCore = pc
        self.Clock = Clock(dt=dt)
        self.Y = None
        self.Equations = eqs
        self.UpdateEnd = 0
        self.ForeignLinks = list()

    def add_observing_stock(self, stock):
        self.Obs.add_observing_stock(stock)

    def add_observing_stock_function(self, func):
        self.Obs.add_observing_stock_function(func)

    def add_observing_flow_function(self, func):
        self.Obs.add_observing_flow_function(func)

    def read_y0(self, y0, ti):
        self.Equations.set_y(y0)
        self.Y = self.Equations.get_y_dict()

    def preset(self, ti):
        self.Clock.initialise(ti)
        self.UpdateEnd = self.TimeEnd = ti
        self.Equations.set_y(self.Y)

    def reset(self, ti):
        self.Clock.initialise(ti)
        self.UpdateEnd = self.TimeEnd = ti
        self.Equations.set_y(self.Y)

    def go_to(self, ti):
        f, t = self.UpdateEnd, ti
        if f is t:
            return
        self.Y = self.Equations.update(t0=f, t1=t, pars=self.PCore)
        self.UpdateEnd = ti
        self.Clock.update(ti)

    def do_request(self, req):
        if req.Time > self.TimeEnd:
            self.go_to(req.Time)

    def find_next(self):
        evt = Event('Update Forward', self.Clock.Next)
        self.Requests.append_event(evt, 'Equation', self.Name)

    def listen(self, mod_src, par_src, par_tar, **kwargs):
        self.ForeignLinks.append(Links(mod_src, par_src, par_tar, kwargs))

    def listen_multi(self, mod_src_all, par_src, par_tar, **kwargs):
        self.ForeignLinks.append(Links(mod_src_all, par_src, par_tar, kwargs))

    def impulse_foreign(self, fore, ti):
        lks = [fl for fl in self.ForeignLinks if fl.mod_src == fore.Name]
        for _, par_src, par_tar in lks:
            val = fore[par_src]
            self.Equations.impulse(par_tar, val)

    def to_json(self):
        # todo
        pass

    def clone(self, **kwargs):
        core = self.Equations.clone(**kwargs)
        pc = kwargs['pc'] if 'pc' in kwargs else self.PCore
        co = ODEModel(self.Name, core, pc, dt=self.Clock.By)
        co.Clock.Initial = self.Clock.Initial
        co.Clock.Last = self.Clock.Last
        co.TimeEnd = self.TimeEnd
        co.UpdateEnd = self.UpdateEnd
        co.Obs.TimeSeries = deepcopy(self.Obs.TimeSeries)
        co.Obs.Last = dict(self.Obs.Last.items())
        co.Y = deepcopy(self.Y)
        core.initialise(co, self.TimeEnd)
        return co



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
        # todo
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
