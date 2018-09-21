from copy import deepcopy
from abc import ABCMeta, abstractmethod
from complexism.misc.counter import count
from complexism.mcore import Observer, LeafModel, ModelAtom, LeafY0
from complexism.element import Event, StepTicker


__author__ = 'TimeWz667'
__all__ = ['AbsEquations', 'ObsEBM', 'GenericEquationBasedModel', 'EBMY0']


class AbsEquations(ModelAtom, metaclass=ABCMeta):
    def __init__(self, name, dt, pars, x=None):
        ModelAtom.__init__(self, name, pars)
        if x:
            self.Attributes.update(x)
        self.Clock = StepTicker(dt=dt)

    def find_next(self):
        return Event('update', self.Clock.Next)

    def update_time(self, ti):
        self.go_to(ti)
        self.Clock.update(ti)
        self.drop_next()

    def execute_event(self):
        self.update_time(self.Next.Time)

    @abstractmethod
    def go_to(self, ti):
        pass

    @abstractmethod
    def set_y(self, y):
        pass

    @abstractmethod
    def get_y_dict(self):
        pass


class EBMY0(LeafY0, metaclass=ABCMeta):
    @abstractmethod
    def get_dict_form(self):
        pass


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
    def __init__(self, name, eqs, pars=None, obs=None, y0_class=None):
        obs = obs if obs else ObsEBM()
        LeafModel.__init__(self, name, pars, obs, y0_class=y0_class if y0_class else LeafY0)
        self.Y = None
        self.Equations = eqs
        self.Scheduler.add_atom(self.Equations)

    def add_observing_stock(self, stock):
        self.Observer.add_observing_stock(stock)

    def add_observing_stock_function(self, func):
        self.Observer.add_observing_stock_function(func)

    def add_observing_flow_function(self, func):
        self.Observer.add_observing_flow_function(func)

    def read_y0(self, y0, ti):
        self.Equations.set_y(y0.get_dict_form())
        self.Y = self.Equations.get_y_dict()

    def preset(self, ti):
        self.Equations.set_y(self.Y)
        self.Equations.initialise(ti, self)
        self.disclose('initialise', '*')
        self.Scheduler.reschedule_all()

    def reset(self, ti):
        self.Equations.reset(ti, self)
        self.Equations.set_y(self.Y)
        self.disclose('reset', '*')
        self.Scheduler.reschedule_all()

    def go_to(self, ti):
        self.Equations.update_time(ti)
        self.Y = self.Equations.get_y_dict()

    def fetch_disclosures(self, ds_ms, time):
        self.go_to(time)
        LeafModel.fetch_disclosures(self, ds_ms, time)

    @count()
    def do_request(self, req):
        self.Equations.execute_event()

    def shock(self, time, action, **values):
        self.Y = self.Equations.shock(None, self, action, **values)

    def to_json(self):
        # todo
        pass

    def clone(self, **kwargs):
        core = self.Equations.clone(**kwargs)
        pc = kwargs['env'] if 'env' in kwargs else self.Environment
        co = GenericEquationBasedModel(self.Name, eqs=core, pars=pc)
        co.TimeEnd = self.TimeEnd
        co.Observer.TimeSeries = deepcopy(self.Observer.TimeSeries)
        co.Observer.Last = dict(self.Observer.Last.items())
        co.Y = deepcopy(self.Y)
        core.initialise(co, self.TimeEnd)
        return co
