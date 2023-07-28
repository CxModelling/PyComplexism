from inspect import signature
import pickle
import epidag as dag
from mcore import AbsModelBlueprint
from .ebm import GenericEquationBasedModel, EBMY0
from .odeebm import OrdinaryDifferentialEquationModel, OrdinaryDifferentialEquations, ODEY0


__author__ = 'TimeWz667'
__all__ = ['BlueprintODEEBM']


class BlueprintODEEBM(AbsModelBlueprint):
    def __init__(self, name):
        AbsModelBlueprint.__init__(self, name)
        self.Arguments['dt'] = 0.1
        self.Arguments['odt'] = 1
        self.ODE = None
        self.Ys = None
        self.Ps = None
        self.Xs = None
        self.ObsYs = list()
        self.Measurements = list()

    def set_fn_ode(self, fn, ys):
        for x, y in zip(signature(fn).parameters.keys(), ['y', 't', 'p', 'x']):
            if x != y:
                raise TypeError('Positional arguments should be y, t, p, and x')
        self.ODE = fn
        self.Ys = list(ys)

    def set_required_parameters(self, ps):
        self.Ps = list(ps)

    def set_external_variables(self, xs):
        self.Xs = dict(xs)

    def add_observing_function(self, fn):
        for x, y in zip(signature(fn).parameters.keys(), ['y', 't', 'p', 'x']):
            if x != y:
                raise TypeError('Positional arguments should be y, t, p, and x')
        self.Measurements.append(fn)

    def set_observations(self, stocks: list = '*'):
        if stocks == '*':
            self.ObsYs = list(self.Ys)
        elif isinstance(stocks, list):
            self.ObsYs = [s for s in stocks if s in self.Ys]

    def set_dt(self, dt=0.1, odt=1):
        if dt <= 0 or odt <= 0:
            raise ValueError('Time differences must be positive numbers')
        dt = min(dt, odt)
        self.Arguments.update({
            'dt': dt,
            'odt': odt
        })

    def get_parameter_hierarchy(self, da=None):
        if self.Ps:
            return {self.Class: self.Ps}
        else:
            return {self.Class: []}

    def get_y0_proto(self):
        return ODEY0()

    def generate(self, name, **kwargs):
        if not all([self.Ys, self.ODE]):
            raise TypeError('Equation have not been assigned')

        # Prepare PC, DC
        if 'pc' in kwargs:
            pc = kwargs['pc']
        elif 'sm' in kwargs:
            sm = kwargs['sm']
            pc = sm.generate(name, exo=kwargs['exo'] if 'exo' in kwargs else None)
        elif 'bn' in kwargs:
            bn = kwargs['bn']
            random = kwargs['random'] if 'random' in kwargs else []
            hie = kwargs['hie'] if 'hie' in kwargs else self.get_parameter_hierarchy()
            sm = dag.as_simulation_core(bn, hie=hie, random=random)
            pc = sm.generate(name, exo=kwargs['exo'] if 'exo' in kwargs else None)
        else:
            raise KeyError('Parameter core not found')

        dt, odt = self.Arguments['dt'], self.Arguments['odt']

        model = OrdinaryDifferentialEquationModel(name, self.ODE, dt, odt, ys=self.Ys, xs=self.Xs, pars=pc)
        model.Class = self.Class
        # Assign observations
        for st in self.ObsYs:
            model.add_observing_stock(st)

        for fn in self.Measurements:
            model.add_observing_function(fn)

        return model

    def to_json(self):
        xs = dict()
        for k, v in self.Xs.items():
            if type(v) in [int, float, str]:
                xs[k] = v
            else:
                xs[k] = pickle.dumps(v)

        return {
            'Class': self.Class,
            'Proto': 'ODEEBM',
            'Arguments': dict(self.Arguments),
            'ODE': pickle.dumps(self.ODE),
            'Ys': self.Ys,
            'Ps': self.Ps,
            'Xs': xs,
            'ObsYs': self.ObsYs,
            'Measurements': [pickle.dumps(m) for m in self.Measurements]
        }

    @staticmethod
    def from_json(js):
        bp = BlueprintODEEBM(js['Class'])
        bp.Arguments.update(js['Arguments'])
        bp.set_fn_ode(pickle.loads(js['ODE']), js['Ys'])
        bp.set_external_variables(js['Xs'])
        bp.set_required_parameters(js['Ps'])
        bp.set_observations([y for y in js['ObsYs']])
        for m in js['Measurements']:
            bp.add_observing_function(pickle.loads(m))
        return bp

    def clone_model(self, mod_src, **kwargs):
        # todo
        pass


class BlueprintEBM(AbsModelBlueprint):
    def __init__(self, name):
        AbsModelBlueprint.__init__(self, name)
        self.YNames = None
        self.InternalVariables = None
        self.Equations = None
        self.ObsStocks = list()
        self.ObsStockFunctions = list()
        self.ObsFlowFunctions = list()

    def set_ode(self, ode):
        self.Equations = ode

    def set_x(self, x):
        self.InternalVariables = dict(x)

    def set_y_names(self, names):
        self.YNames = list(names)

    def set_observations(self, stocks=None, stock_functions=None, flow_functions=None):
        if stocks:
            self.ObsStocks = list(stocks)
        if stock_functions:
            self.ObsStockFunctions = list(stock_functions)
        if flow_functions:
            self.ObsFlowFunctions = list(flow_functions)

    def generate(self, name, **kwargs):
        if not self.Equations:
            raise AttributeError('Equation loss')
        if not self.YNames:
            raise AttributeError('Y names undefined')

        # Prepare PC
        if 'pc' in kwargs:
            pc = kwargs['pc']
        elif 'sm' in kwargs:
            sm = kwargs['sm']
            pc = sm.generate(name, exo=kwargs['exo'] if 'exo' in kwargs else None)
        elif 'bn' in kwargs:
            bn = kwargs['bn']
            random = kwargs['random'] if 'random' in kwargs else list()
            hie = kwargs['hie'] if 'hie' in kwargs else self.get_parameter_hierarchy()
            sm = dag.as_simulation_core(bn, hie=hie, random=random, out=list())
            pc = sm.generate(name, exo=kwargs['exo'] if 'exo' in kwargs else None)
        else:
            raise KeyError('Parameter core not found')

        self.Arguments.update(kwargs)

        # Generate model
        dt = self.Arguments['dt'] if 'dt' in self.Arguments else 0.5
        fdt = self.Arguments['fdt'] if 'fdt' in self.Arguments else dt
        eqs = OrdinaryDifferentialEquations(name,
                                            self.Equations,
                                            self.YNames,
                                            fdt=fdt,
                                            dt=dt,
                                            pars=pc,
                                            x=self.InternalVariables)

        model = GenericEquationBasedModel(name, eqs=eqs, pars=pc)

        # Decide outputs
        for st in self.ObsStocks:
            model.add_observing_stock(st)
        for func in self.ObsStockFunctions:
            model.add_observing_stock_function(func)
        for func in self.ObsFlowFunctions:
            model.add_observing_flow_function(func)

        return model

    @staticmethod
    def from_json(js):
        # todo
        pass

    def get_parameter_hierarchy(self, da=None):
        return {self.Class: []}

    def get_y0_proto(self):
        return EBMY0()

    def to_json(self):
        # todo
        pass

    def clone_model(self, mod_src, **kwargs):
        # todo
        pass
