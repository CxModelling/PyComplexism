import numpy as np
from scipy.integrate import odeint
from mcore import Observer
from .ebm import AbsEquations, GenericEquationBasedModel, EBMY0

__author__ = 'TimeWz667'
__all__ = ['ObsODE', 'ODEY0', 'OrdinaryDifferentialEquations', 'OrdinaryDifferentialEquationModel']


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
        p = model.Parameters
        x = model.Equations.Attributes

        for func in self.Functions:
            tab.update(func(y=y, t=tiu, p=p, x=x))


class OrdinaryDifferentialEquations(AbsEquations):
    def __init__(self, name, fn, y_names, dt, fdt, pars, x=None):
        AbsEquations.__init__(self, name, dt, pars, x)
        self.Y = np.zeros(len(y_names))
        self.NamesY = y_names
        self.IndicesY = {v: i for i, v in enumerate(y_names)}
        self.Func = fn
        self.Fdt = fdt
        self.Last = None

    def initialise(self, ti, model, *args, **kwargs):
        self.Last = ti

    def reset(self, ti, model, *args, **kwargs):
        self.Last = ti

    def set_external_variables(self, xs):
        """
        Set external variables by importing a dictionary
        :param xs: external variables
        :type xs: dict
        """
        try:
            self.Attributes.update(xs)
        except AttributeError as e:
            raise e

    def set_y(self, y):
        try:
            y = y.Ys
        except AttributeError:
            pass
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

    def go_to(self, ti):
        t0, t1 = self.Last, ti
        if t0 == t1:
            return
        num = max(int((t1 - t0) / self.Fdt) + 1, 2)
        ts = np.linspace(t0, t1, num)
        self.Y = odeint(self.Func, self.Y, ts, args=(self.Parameters, self.Attributes))[-1]
        self.Last = t1

    def shock(self, ti, model, action, **values):
        if action == 'impulse':
            try:
                k, v1 = values['k'], values['v']
                v0 = self[k]
                self[k] = v1
                model.disclose('change {} from {} to {}'.format(k, v0, v1), 'Equation')
            except KeyError:
                raise KeyError('Unmatched keywords')
        elif action == 'add':
            try:
                y = values['y']
                if y not in self.IndicesY:
                    raise KeyError('{} does not exist')
                n = values['n'] if 'n' in values else 1
                self.Y[self.IndicesY[y]] += n
                model.disclose('add {} by {}'.format(y, n), 'Equation')
            except KeyError:
                raise KeyError('Unmatched keywords')
        elif action == 'del':
            try:
                y = values['y']
                if y not in self.IndicesY:
                    raise KeyError('{} does not exist')

                n = values['n'] if 'n' in values else 1
                n = min(n, np.floor(self.Y[self.IndicesY[y]]))
                self.Y[self.IndicesY[y]] -= n
                model.disclose('delete {} by {}'.format(y, n), 'Equation')
            except KeyError:
                raise KeyError('Unmatched keywords')
        else:
            raise ValueError('Non-identifiable event')

        return self.get_y_dict()


class ODEY0(EBMY0):
    def __init__(self):
        EBMY0.__init__(self)

    def get_dict_form(self):
        return {ent['st']: ent['n'] for ent in self.Entries}

    def match_model_info(self, model):
        yns = model.Equations.NamesY
        ys = [ent['st'] for ent in self.Entries]
        for yn in yns:
            if yn not in ys:
                self.Entries.append({'st': yn, 'n': 0})

    def define(self, st, n=1, **kwargs):
        EBMY0.define(self, st=st, n=n, **kwargs)

    @staticmethod
    def from_source(src):
        y0 = ODEY0()
        y0.Entries = list(src.Entries)
        return y0

    @staticmethod
    def from_json(js):
        return EBMY0.from_json(js)


class OrdinaryDifferentialEquationModel(GenericEquationBasedModel):
    def __init__(self, name, fn, dt, odt, ys, xs=None, pars=None):
        dt = min(dt, odt)
        eqs = OrdinaryDifferentialEquations(name, fn, ys, odt, fdt=dt, pars=pars, x=xs)
        GenericEquationBasedModel.__init__(self, name, eqs, pars=pars, obs=ObsODE(), y0_class=ODEY0)

    def add_observing_flow_function(self, func):
        raise TypeError('Depreciated method in ODE model, try add_observing_function')

    def add_observing_stock_function(self, func):
        raise TypeError('Depreciated method in ODE model, try add_observing_function')

    def add_observing_function(self, func):
        self.Observer.add_observing_function(func)
