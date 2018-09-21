from abc import ABCMeta, abstractmethod
import numpy.random as rd
from complexism.element import Event, StepTicker
from ..modifier import GloRateModifier, LocRateModifier, BuffModifier, NerfModifier
from .behaviour import PassiveModBehaviour, ActiveModBehaviour
from .trigger import StateTrigger
__author__ = 'TimeWz667'
__all__ = ['ExternalShock',
           'FDShock', 'FDShockFast', 'DDShock', 'DDShockFast',
           'WeightedSumShock', 'WeightedAvgShock',
           'NetShock', 'NetWeightShock',
           'SwitchOn', 'SwitchOff']


class ExternalShock(PassiveModBehaviour):
    def __init__(self, t_tar):
        mod = GloRateModifier(t_tar)
        PassiveModBehaviour.__init__(self, mod)
        self.T_tar = t_tar
        self.Value = 1

    def initialise(self, ti, model):
        self.__shock(model, ti)

    def reset(self, ti, model):
        pass

    def shock(self, ti, model, action, **values):
        self.Value = values['v']
        self.__shock(model, ti)

    def match(self, be_src, ags_src, ags_new, ti):
        self.Value = be_src.Value
        for ag in ags_new.values():
            self.register(ag, ti)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value

    def __shock(self, model, ti):
        self.ProtoModifier.Value = self.Value
        for ag in model.agents:
            ag.modify(self.Name, ti)


class GlobalShock(PassiveModBehaviour, metaclass=ABCMeta):
    def __init__(self, s_src, t_tar):
        tri = StateTrigger(s_src)
        mod = GloRateModifier(t_tar)
        PassiveModBehaviour.__init__(self, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Value = 0

    def initialise(self, ti, model):
        self.Value = self._evaluate(model)
        self.__shock(model, ti)

    def reset(self, ti, model):
        pass

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        self.Value = self._evaluate(model)
        self.__shock(model, ti)

    def impulse_enter(self, model, ag, ti, args=None):
        self.Value += self._difference(model, ag)
        self.__shock(model, ti)

    def impulse_exit(self, model, ag, ti, args=None):
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


class GlobalShockFast(ActiveModBehaviour):
    def __init__(self,  s_src, t_tar, dt):
        mod = GloRateModifier( t_tar)
        ActiveModBehaviour.__init__(self, StepTicker(dt=dt), mod)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Value = 0

    def initialise(self, ti, model):
        ActiveModBehaviour.initialise(self, ti, model)
        self.Value = self._evaluate(model)
        self.__shock(model, ti)

    def reset(self, ti, model):
        self.Clock.initialise(ti)
        self.Value = self._evaluate(model)
        self.__shock(model, ti)

    def compose_event(self, ti):
        return Event('update value', ti)

    def do_action(self, model, todo, ti):
        self.Value = self._evaluate(model)
        self.__shock(model, ti)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value

    def match(self, be_src, ags_src, ags_new, ti):
        self.Value = be_src.Value
        for ag in ags_new.values():
            self.register(ag, ti)

    def __shock(self, model, ti):
        if self.ProtoModifier.Value is not self.Value:
            self.ProtoModifier.Value = self.Value
            for ag in model.agents:
                ag.modify(self.Name, ti)
            model.disclose('update value', self.Name)

    @abstractmethod
    def _evaluate(self, model):
        pass


class FDShock(GlobalShock):
    def _evaluate(self, model):
        return model.Population.count(st=self.S_src) / len(model)

    def _difference(self, model, ag):
        return 1 / len(model)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Value
        return 'FDShock({}, {} on {}, by={})'.format(*opt)


class FDShockFast(GlobalShockFast):
    def _evaluate(self, model):
        return model.Population.count(st=self.S_src) / len(model)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Value
        return 'FDShockFast({}, {} on {}, by={})'.format(*opt)


class DDShock(GlobalShock):
    def _evaluate(self, model):
        return model.Population.count(st=self.S_src)

    def _difference(self, model, ag):
        return 1

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Value
        return 'DDShock({}, {} on {}, by={})'.format(*opt)


class DDShockFast(GlobalShockFast):
    def _evaluate(self, model):
        return model.Population.count(st=self.S_src)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Value
        return 'DDShockFast({}, {} on {}, by={})'.format(*opt)


class WeightedSumShock(GlobalShockFast):
    def __init__(self, s_src, t_tar, weight, dt):
        GlobalShockFast.__init__(self, s_src, t_tar, dt)
        self.Weight = weight

    def _evaluate(self, model):
        val = 0
        for k, v in self.Weight.items():
            val = model.Population.count(st=self.S_src) * v
        return val

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value

    def match(self, be_src, ags_src, ags_new, ti):
        self.Value = be_src.Value
        for ag in ags_new.values():
            self.register(ag, ti)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Value
        return 'WeightedSumShock({}, {} on {}, by={})'.format(*opt)


class WeightedAvgShock(GlobalShockFast):
    def __init__(self, s_src, t_tar, weight, dt):
        GlobalShockFast.__init__(self, s_src, t_tar, dt)
        self.Weight = weight

    def _evaluate(self, model):
        val = 0
        for k, v in self.Weight.items():
            val = model.Population.count(st=self.S_src) * v
        return val/len(model)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value

    def match(self, be_src, ags_src, ags_new, ti):
        self.Value = be_src.Value
        for ag in ags_new.values():
            self.register(ag, ti)

    def clone(self, *args, **kwargs):
        pass

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Value
        return 'WeightAvgShock({}, {} on {}, by={})'.format(*opt)


class NetShock(PassiveModBehaviour, metaclass=ABCMeta):
    def __init__(self, s_src, t_tar, net):
        tri = StateTrigger(s_src)
        mod = LocRateModifier(t_tar)
        PassiveModBehaviour.__init__(self, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Net = net

    def initialise(self, ti, model):
        for ag in model.agents:
            val = model.Population.count_neighbours(ag, st=self.S_src, net=self.Net)
            ag.shock(ti, None, self.Name, value=val)

    def reset(self, ti, model):
        pass

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        self.__shock(ag, model, ti)

    def impulse_enter(self, model, ag, ti, args=None):
        self.__shock(ag, model, ti)

    def impulse_exit(self, model, ag, ti, args=None):
        self.__shock(ag, model, ti)

    def match(self, be_src, ags_src, ags_new, ti):
        for ag_new, ag_src in zip(ags_new.values(), ags_src.values()):
            self.register(ag_new, ti)
            ag_new.set_mod_value(self.Name, ag_src.get_mod_value(self.Name))

    def fill(self, obs, model, ti):
        vs = 0
        for ag in model.agents:
            vs += ag.Modifiers[self.Name].Value
        try:
            obs[self.Name] = vs / len(model.agents)
        except ZeroDivisionError:
            obs[self.Name] = 0

    def __shock(self, ag, model, ti):
        val = model.Population.count_neighbours(ag, st=self.S_src, net=self.Net)
        ag.shock(ti, None, self.Name, value=val)
        for nei in model.Population.neighbours(ag, net=self.Net):
            val = model.Population.count_neighbours(nei, st=self.S_src, net=self.Net)
            nei.shock(ti, None, self.Name, value=val)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Net
        return 'NetShock({}, {} on {} of {})'.format(*opt)


class NetWeightShock(PassiveModBehaviour, metaclass=ABCMeta):
    def __init__(self, s_src, t_tar, net, weight):
        tri = StateTrigger(s_src)
        mod = LocRateModifier(t_tar)
        PassiveModBehaviour.__init__(self, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Net = net
        self.Weight = weight

    def initialise(self, ti, model):
        for ag in model.agents:
            val = self.__foi(ag, model)
            ag.shock(ti, None, self.Name, val)

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        self.__shock(ag, model, ti)

    def impulse_enter(self, model, ag, ti, args=None):
        self.__shock(ag, model, ti)

    def impulse_exit(self, model, ag, ti, args=None):
        self.__shock(ag, model, ti)

    def match(self, be_src, ags_src, ags_new, ti):
        for ag_new, ag_src in zip(ags_new.values(), ags_src.values()):
            self.register(ag_new, ti)
            ag_new.set_mod_value(self.Name, ag_src.get_mod_value(self.Name))

    def fill(self, obs, model, ti):
        vs = 0
        for ag in model.agents:
            vs += ag.Mods[self.Name].Value
        try:
            obs[self.Name] = vs / len(model.agents)
        except ZeroDivisionError:
            obs[self.Name] = 0

    def __foi(self, ag, model):
        val = 0
        for k, v in self.Weight.items():
            model.Population.count_neighbours(ag, st=k, net=self.Net) * v
        return val

    def __shock(self, ag, model, ti):
        val = self.__foi(ag, model)
        ag.shock(ti, self.Name, self.Name, value=val)
        for nei in model.Population.neighbours(ag, net=self.Net):
            val = self.__foi(nei, model)
            nei.shock(ti, self.Name, self.Name, value=val)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Net
        return 'NetWeightShock({}, {} on {} of {})'.format(*opt)


class SwitchOn(PassiveModBehaviour, metaclass=ABCMeta):
    def __init__(self, s_src, t_tar, prob):
        tri = StateTrigger(s_src)
        mod = BuffModifier(t_tar)
        PassiveModBehaviour.__init__(self, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Prob = prob
        self.Decision = 0
        self.Buff = 0

    def initialise(self, ti, model):
        for ag in model.agents:
            if self.S_src in ag.State:
                self.__shock(ag, ti)

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        self.__shock(ag, ti)

    def impulse_enter(self, model, ag, ti, args=None):
        self.__shock(ag, ti)

    def impulse_exit(self, model, ag, ti, args=None):
        ag.shock(ti, self.Name, self.Name, False)

    def match(self, be_src, ags_src, ags_new, ti):
        for ag_new, ag_src in zip(ags_new.values(), ags_src.values()):
            self.register(ag_new, ti)
            ag_new.set_mod_value(self.Name, ag_src.get_mod_value(self.Name))

    def fill(self, obs, model, ti):
        try:
            obs[self.Name] = self.Buff / self.Decision
        except ZeroDivisionError:
            obs[self.Name] = 0

    def __shock(self, ag, ti):
        self.Decision += 1

        if rd.random() < self.Prob:
            ag.shock(ti, self.Name, self.Name, value=True)
            self.Buff += 1
        else:
            ag.shock(ti, self.Name, self.Name, value=False)


class SwitchOff(PassiveModBehaviour, metaclass=ABCMeta):
    def __init__(self, s_src, t_tar, prob):
        tri = StateTrigger(s_src)
        mod = NerfModifier(t_tar)
        PassiveModBehaviour.__init__(self, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Prob = prob
        self.Decision = 0
        self.Nerf = 0

    def initialise(self, ti, model):
        for ag in model.agents:
            if self.S_src in ag.State:
                self.__shock(ag, ti)

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        self.__shock(ag, ti)

    def impulse_enter(self, model, ag, ti, args=None):
        self.__shock(ag, ti)

    def impulse_exit(self, model, ag, ti, args=None):
        ag.shock(ti, self.Name, self.Name, False)

    def match(self, be_src, ags_src, ags_new, ti):
        for ag_new, ag_src in zip(ags_new.values(), ags_src.values()):
            self.register(ag_new, ti)
            ag_new.set_mod_value(self.Name, ag_src.get_mod_value(self.Name))

    def fill(self, obs, model, ti):
        try:
            obs[self.Name] = self.Nerf / self.Decision
        except ZeroDivisionError:
            obs[self.Name] = 0

    def __shock(self, ag, ti):
        self.Decision += 1
        if rd.random() < self.Prob:
            ag.shock(ti, self.Name, self.Name, value=True)
            self.Nerf += 1
        else:
            ag.shock(ti, self.Name, self.Name, value=False)
