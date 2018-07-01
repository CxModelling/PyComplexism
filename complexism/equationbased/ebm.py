import numpy as np
from copy import deepcopy
from scipy.integrate import odeint
from abc import ABCMeta, abstractmethod
from complexism.misc.counter import count
from complexism.mcore import Observer, LeafModel
from complexism.element import Clock, Event


__author__ = 'TimeWz667'
__all__ = ['AbsEquations', 'OrdinaryDifferentialEquations',
           'ObsEBM', 'GenericEquationBasedModel']


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

    def execute_event(self, model, event, *args, **kwargs):
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

    def set_external_variables(self, xs):
        """
        Set external variables by importing a dictionary
        :param xs: external variables
        :type xs: dict
        """
        try:
            self.X.update(xs)
        except AttributeError as e:
            raise e

    def set_y(self, y):
        n = len(self.NamesY)
        if len(y) is not n:
            raise AttributeError

        if isinstance(y, list):
            self.Y = np.array(y)
        else:
            self.Y = np.zeros(n)
            for k, i in self.IndicesY.items():
                try:
                    self.Y[i] = y[k]
                except KeyError:
                    self.Y[i] = 0

    def get_y_dict(self):
        return {v: self.Y[i] for v, i in self.IndicesY.items()}

    def update(self, t0, t1, pars):
        num = max(int((t1 - t0) / self.Dt) + 1, 2)
        ts = np.linspace(t0, t1, num)
        self.Y = odeint(self.Func, self.Y, ts, args=(pars, self.X))[-1]
        return self.get_y_dict()

    def execute_event(self, model, event, **kwargs):
        if event == 'impulse':
            try:
                k, v1 = kwargs['k'], kwargs['v']
                v0 = self.X[k]
                self.X[k] = v1
                model.disclose('change {} from {} to {}'.format(k, v0, v1), 'Equation')
            except KeyError:
                raise KeyError('Unmatched keywords')
        elif event == 'add':
            try:
                y = kwargs['y']
                if y not in self.IndicesY:
                    raise KeyError('{} does not exist')
                n = kwargs['n'] if 'n' in kwargs else 1
                self.Y[self.IndicesY[y]] += n
                model.disclose('add {} by {}'.format(y, n), 'Equation')
            except KeyError:
                raise KeyError('Unmatched keywords')
        elif event == 'del':
            try:
                y = kwargs['y']
                if y not in self.IndicesY:
                    raise KeyError('{} does not exist')

                n = kwargs['n'] if 'n' in kwargs else 1
                n = min(n, np.floor(self.Y[self.IndicesY[y]]))
                self.Y[self.IndicesY[y]] -= n
                model.disclose('delete {} by {}'.format(y, n), 'Equation')
            except KeyError:
                raise KeyError('Unmatched keywords')
        else:
            raise ValueError('Non-identifiable event')

        return self.get_y_dict()


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
        if tab is self.Mid:
            tiu = ti - self.ObservationalInterval/2
        else:
            tiu = ti
        model.go_to(tiu)
        for st in self.Stocks:
            tab[st] = model.Y[st]

        for func in self.StockFunctions:
            func(model, tab, tiu)


class GenericEquationBasedModel(LeafModel):
    def __init__(self, name, eqs, dt, env=None, obs=None, y0_class=None):
        obs = obs if obs else ObsEBM()
        LeafModel.__init__(self, name, env, obs, y0_class=y0_class)
        self.Clock = Clock(dt=dt)
        self.Y = None
        self.Equations = eqs
        self.UpdateEnd = 0

    def add_observing_stock(self, stock):
        self.Observer.add_observing_stock(stock)

    def add_observing_stock_function(self, func):
        self.Observer.add_observing_stock_function(func)

    def add_observing_flow_function(self, func):
        self.Observer.add_observing_flow_function(func)

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
        if f == t:
            return
        self.Y = self.Equations.update(t0=f, t1=t, pars=self.Environment)
        self.UpdateEnd = ti
        self.Clock.update(ti)

    @count()
    def do_request(self, req):
        if req.When > self.UpdateEnd:
            self.go_to(req.When)

    def find_next(self):
        evt = Event('update', self.Clock.Next, 'update')
        self.request(evt, 'Equation')

    def impulse(self, action, **kwargs):
        self.Y = self.Equations.execute_event(self, action, **kwargs)

    def to_json(self):
        # todo
        pass

    def clone(self, **kwargs):
        core = self.Equations.clone(**kwargs)
        pc = kwargs['env'] if 'env' in kwargs else self.Environment
        co = GenericEquationBasedModel(self.Name, dt=self.Clock.By, eqs=core, env=pc)
        co.Clock.Initial = self.Clock.Initial
        co.Clock.Last = self.Clock.Last
        co.TimeEnd = self.TimeEnd
        co.UpdateEnd = self.UpdateEnd
        co.Observer.TimeSeries = deepcopy(self.Observer.TimeSeries)
        co.Observer.Last = dict(self.Observer.Last.items())
        co.Y = deepcopy(self.Y)
        core.initialise(co, self.TimeEnd)
        return co
