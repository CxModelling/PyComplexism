from abc import ABCMeta, abstractmethod
from complexism.element import Event, Clock
from ..modifier import GloRateModifier
from .behaviour import TimeIndModBehaviour, TimeDepModBehaviour
from .trigger import StateTrigger
__author__ = 'TimeWz667'
__all__ = ['FDShock', 'FDShockFast', 'DDShock', 'DDShockFast']


class GlobalShock(TimeIndModBehaviour, metaclass=ABCMeta):
    def __init__(self, name, s_src, t_tar):
        tri = StateTrigger(s_src)
        mod = GloRateModifier(name, t_tar)
        TimeIndModBehaviour.__init__(self, name, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Value = 0

    def initialise(self, time, model, *args, **kwargs):
        self.Value = self._evaluate(model)
        self.__shock(model, time)

    def impulse_change(self, model, ag, ti):
        self.Value = self._evaluate(model)
        self.__shock(model, ti)

    def impulse_enter(self, model, ag, ti):
        self.Value += self._difference(model, ag)
        self.__shock(model, ti)

    def impulse_exit(self, model, ag, ti):
        self.Value -= self._difference(model, ag)
        self.__shock(model, ti)

    def match(self, be_src, ags_src, ags_new, ti):
        self.Value = be_src.Value
        for ag in ags_new.values():
            self.register(ag, ti)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value

    @abstractmethod
    def _evaluate(self, model):
        pass

    @abstractmethod
    def _difference(self, model, ag):
        pass

    def __shock(self, model, ti):
        self.ProtoModifier.Value = self.Value
        for ag in model.agents:
            ag.modify(self.Name, ti)


class GlobalShockFast(TimeDepModBehaviour):
    def __init__(self, name, s_src, t_tar, dt):
        mod = GloRateModifier(name, t_tar)
        TimeDepModBehaviour.__init__(self, name, Clock(dt=dt), mod)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Value = 0

    def initialise(self, time, *args, **kwargs):
        TimeDepModBehaviour.initialise(self, time, *args, **kwargs)
        model = kwargs['model']
        self.Value = self._evaluate(model)
        self.__shock(model, time)

    def reset(self, time, *args, **kwargs):
        self.Clock.initialise(time)
        model = kwargs['model']
        self.Value = self._evaluate(model)
        self.__shock(model, time)

    def compose_event(self, time):
        return Event(self.Name, time)

    def do_action(self, model, todo, time):
        self.Value = self._evaluate(model)
        self.__shock(model, time)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value

    def match(self, be_src, ags_src, ags_new, ti):
        self.Value = be_src.Value
        for ag in ags_new.values():
            self.register(ag, ti)

    def __shock(self, model, ti):
        self.ProtoModifier.Value = self.Value
        for ag in model.agents:
            ag.modify(self.Name, ti)

    @abstractmethod
    def _evaluate(self, model):
        pass


class FDShock(GlobalShock):
    def _evaluate(self, model):
        return model.Population.count(st=self.S_src) / len(model)

    def _difference(self, model, ag):
        return 1 / len(model)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        model.Behaviours[name] = FDShock(name, s_src, t_tar)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Value
        return 'FDShock({}, {} on {}, by={})'.format(*opt)


class FDShockFast(GlobalShockFast):
    def _evaluate(self, model):
        return model.Population.count(st=self.S_src) / len(model)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        dt = kwargs['dt'] if 'dt' in kwargs else 1
        model.Behaviours[name] = FDShockFast(name, s_src, t_tar, dt)

    def clone(self, *args, **kwargs):
        pass

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Value
        return 'FDShockFast({}, {} on {}, by={})'.format(*opt)


class DDShock(GlobalShock):
    def _evaluate(self, model):
        return model.Population.count(st=self.S_src)

    def _difference(self, model, ag):
        return 1

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        model.Behaviours[name] = DDShock(name, s_src, t_tar)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Value
        return 'DDShock({}, {} on {}, by={})'.format(*opt)


class DDShockFast(GlobalShockFast):
    def _evaluate(self, model):
        return model.Population.count(st=self.S_src)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        dt = kwargs['dt'] if 'dt' in kwargs else 1
        model.Behaviours[name] = DDShockFast(name, s_src, t_tar, dt)

    def clone(self, *args, **kwargs):
        pass

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Value
        return 'DDShockFast({}, {} on {}, by={})'.format(*opt)
