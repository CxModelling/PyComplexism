import numpy as np
from scipy.integrate import odeint
from .ebm import AbsEquations, GenericEquationBasedModel
from complexism.mcore import Observer, LeafY0

__author__ = 'TimeWz667'


class ObsODE(Observer):
    def __init__(self):
        Observer.__init__(self)
        self.Stocks = list()
        self.Functions = list()

    def add_observing_stock(self, stock):
        self.Stocks.append(stock)

    def add_observing_function(self, func):
        self.Functions.append(func)

    def update_dynamic_observations(self, model, flow, ti):
        model.go_to(ti)
        # for func in self.FlowFunctions:
        #    func(model, flow, ti)

    def read_statics(self, model, tab, ti):
        if tab is self.Mid:
            tiu = ti - self.ObservationalInterval/2
        else:
            tiu = ti
        model.go_to(tiu)
        for st in self.Stocks:
            tab[st] = model.Y[st]

        y = model.Equations.Y
        p = model.Environment
        x = model.Equations.X

        for func in self.Functions:
            tab.update(func(y=y, t=tiu, p=p, x=x))


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
        if isinstance(y, ODEY0):
            self.Y = np.zeros(len(y.Ys))
            for k, v in y:
                self.Y[self.IndicesY[k]] = v
            return

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


class ODEY0(LeafY0):
    def __init__(self):
        LeafY0.__init__(self)
        self.Ys = dict()

    def __iter__(self):
        return iter(self.Ys.items())

    def match_model(self, model):
        yns = model.Equations.NamesY
        for yn in yns:
            if yn not in self.Ys:
                self.Ys[yn] = 0

    def define(self, st, n, *args, **kwargs):
        self.Ys[st] = n

    @staticmethod
    def from_source(src):
        y0 = ODEY0()
        y0.Ys.update(src)
        return y0


class OrdinaryDifferentialEquationModel(GenericEquationBasedModel):
    def __init__(self, name, fn, dt, odt, ys, xs=None, env=None):
        dt = min(dt, odt)
        eqs = OrdinaryDifferentialEquations(fn, ys, dt, x=xs)
        GenericEquationBasedModel.__init__(self, name, eqs, odt, env=env, obs=ObsODE(), y0_class=ODEY0)

    def add_observing_flow_function(self, func):
        raise TypeError('Depreciated method in ODE model, try add_observing_function')

    def add_observing_stock_function(self, func):
        raise TypeError('Depreciated method in ODE model, try add_observing_function')

    def add_observing_function(self, func):
        self.Observer.add_observing_function(func)
