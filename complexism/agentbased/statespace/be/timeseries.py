from complexism.element import Event, Clock
from ..modifier import GloRateModifier
from .behaviour import ActiveModBehaviour

__author__ = 'TimeWz667'
__all__ = ['TimeVarying']


class TimeVarying(ActiveModBehaviour):
    def __init__(self, name, func, t_tar, dt):
        mod = GloRateModifier(name, t_tar)
        ActiveModBehaviour.__init__(self, name, Clock(dt), mod)
        self.Func = func
        self.T_tar = t_tar
        self.Value = 1

    def initialise(self, ti, model):
        self.Value = self.Func(ti)
        self.__shock(model, ti)

    def reset(self, ti, model):
        self.Value = self.Func(ti)
        self.__shock(model, ti)

    def compose_event(self, ti):
        return Event('update value', self.Clock.Next)

    def do_action(self, model, td, ti):
        self.Value = self.Func(ti)
        self.__shock(model, ti)

    def match(self, be_src, ags_src, ags_new, ti):
        self.Value = be_src.Value
        for ag in ags_new.values():
            self.register(ag, ti)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Func(ti)

    def __shock(self, model, ti):
        self.Value = self.Func(ti)
        self.ProtoModifier.Value = self.Value
        for ag in model.agents:
            ag.modify(self.Name, ti)

    @staticmethod
    def decorate(name, model, **kwargs):
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        func = kwargs['func']
        dt = kwargs['dt'] if 'dt' in kwargs else 1
        model.add_behaviour(TimeVarying(name, func, t_tar, dt))
