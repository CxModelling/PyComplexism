import epidag as dag
import complexism as cx
from complexism.mcore import AbsBlueprintMCore
__author__ = 'TimeWz667'
__all__ = ['BlueprintODE']


class BlueprintODE(AbsBlueprintMCore):
    def __init__(self, name):
        AbsBlueprintMCore.__init__(self, name)
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
        eqs = cx.OrdinaryDifferentialEquations(self.Equations,
                                               self.YNames,
                                               dt=fdt,
                                               x=self.InternalVariables)

        model = cx.GenericEquationBasedModel(self.Name, pc, eqs, dt=dt)

        # Decide outputs
        for st in self.ObsStocks:
            model.add_observing_stock(st)
        for func in self.ObsStockFunctions:
            model.add_observing_stock_function(func)
        for func in self.ObsFlowFunctions:
            model.add_observing_flow_function(func)

        return model

    def from_json(self, js):
        # todo
        pass

    def get_parameter_hierarchy(self, **kwargs):
        return {self.Name: []}

    def to_json(self):
        # todo
        pass

    def clone(self, mod_src, **kwargs):
        # todo
        pass
