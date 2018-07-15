from abc import ABCMeta, abstractmethod
import numpy.random as rd
from complexism.element import Event, Clock
from ..modifier import GloRateModifier, LocRateModifier, BuffModifier, NerfModifier
from .behaviour import PassiveModBehaviour, ActiveModBehaviour
from .trigger import StateTrigger
__author__ = 'TimeWz667'
__all__ = ['ExternalShock',
           'FDShock', 'FDShockFast', 'DDShock', 'DDShockFast',
           'WeightSumShock', 'WeightAvgShock',
           'NetShock', 'NetWeightShock',
           'SwitchOn', 'SwitchOff']


class ExternalShock(PassiveModBehaviour):
    def __init__(self, name, t_tar):
        mod = GloRateModifier(name, t_tar)
        PassiveModBehaviour.__init__(self, name, mod)
        self.T_tar = t_tar
        self.Value = 1

    def initialise(self, ti, model, *args, **kwargs):
        self.__shock(model, ti)

    def reset(self, ti, *args, **kwargs):
        pass

    def shock(self, ti, source, target, value):
        self.Value = value
        self.__shock(target, ti)

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

    @staticmethod
    def decorate(name, model, **kwargs):
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        model.Behaviours[name] = ExternalShock(name, t_tar)


class GlobalShock(PassiveModBehaviour, metaclass=ABCMeta):
    def __init__(self, name, s_src, t_tar):
        tri = StateTrigger(s_src)
        mod = GloRateModifier(name, t_tar)
        PassiveModBehaviour.__init__(self, name, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Value = 0

    def initialise(self, ti, model, *args, **kwargs):
        self.Value = self._evaluate(model)
        self.__shock(model, ti)

    def reset(self, ti, *args, **kwargs):
        pass

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


class GlobalShockFast(ActiveModBehaviour):
    def __init__(self, name, s_src, t_tar, dt):
        mod = GloRateModifier(name, t_tar)
        ActiveModBehaviour.__init__(self, name, Clock(dt=dt), mod)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Value = 0

    def initialise(self, ti, *args, **kwargs):
        ActiveModBehaviour.initialise(self, ti, *args, **kwargs)
        model = kwargs['model']
        self.Value = self._evaluate(model)
        self.__shock(model, ti)

    def reset(self, ti, *args, **kwargs):
        self.Clock.initialise(ti)
        model = kwargs['model']
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


class WeightSumShock(GlobalShockFast):
    def __init__(self, name, s_src, t_tar, weight, dt):
        GlobalShockFast.__init__(self, name, s_src, t_tar, dt)
        self.Weight = weight

    def _evaluate(self, model):
        val = 0
        for k, v in self.Weight.items():
            val = model.Population.count(st=self.S_src) * v
        return val

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        dt = kwargs['dt'] if 'dt' in kwargs else 1
        wt = kwargs['weight']
        wt = {model.DCore.States[k]: v for k, v in wt.items()}
        model.Behaviours[name] = WeightSumShock(name, s_src, t_tar, wt, dt)

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
        return 'WeightSumShock({}, {} on {}, by={})'.format(*opt)


class WeightAvgShock(GlobalShockFast):
    def __init__(self, name, s_src, t_tar, weight, dt):
        GlobalShockFast.__init__(self, name, s_src, t_tar, dt)
        self.Weight = weight

    def _evaluate(self, model):
        val = 0
        for k, v in self.Weight.items():
            val = model.Population.count(st=self.S_src) * v
        return val/len(model)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        dt = kwargs['dt'] if 'dt' in kwargs else 1
        wt = kwargs['weight']
        wt = {model.DCore.States[k]: v for k, v in wt.items()}
        model.Behaviours[name] = WeightAvgShock(name, s_src, t_tar, wt, dt)

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
    def __init__(self, name, s_src, t_tar, net):
        tri = StateTrigger(s_src)
        mod = LocRateModifier(name, t_tar)
        PassiveModBehaviour.__init__(self, name, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Net = net

    def initialise(self, ti, model, *args, **kwargs):
        for ag in model.agents:
            val = model.Population.count_neighbours(ag, st=self.S_src, net=self.Net)
            ag.shock(ti, None, self.Name, val)

    def reset(self, ti, *args, **kwargs):
        pass

    def impulse_change(self, model, ag, ti):
        self.__shock(ag, model, ti)

    def impulse_enter(self, model, ag, ti):
        self.__shock(ag, model, ti)

    def impulse_exit(self, model, ag, ti):
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
        ag.shock(ti, None, self.Name, val)
        for nei in model.Population.neighbours(ag, net=self.Net):
            val = model.Population.count_neighbours(nei, st=self.S_src, net=self.Net)
            nei.shock(ti, None, self.Name, val)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Net
        return 'NetShock({}, {} on {} of {})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        model.Behaviours[name] = NetShock(name, s_src, t_tar, kwargs['net'])


class NetWeightShock(PassiveModBehaviour, metaclass=ABCMeta):
    def __init__(self, name, s_src, t_tar, net, weight):
        tri = StateTrigger(s_src)
        mod = LocRateModifier(name, t_tar)
        PassiveModBehaviour.__init__(self, name, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Net = net
        self.Weight = weight

    def initialise(self, ti, model, *args, **kwargs):
        for ag in model.agents:
            val = self.__foi(ag, model)
            ag.shock(ti, None, self.Name, val)

    def impulse_change(self, model, ag, ti):
        self.__shock(ag, model, ti)

    def impulse_enter(self, model, ag, ti):
        self.__shock(ag, model, ti)

    def impulse_exit(self, model, ag, ti):
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
        ag.shock(ti, self.Name, self.Name, val)
        for nei in model.Population.neighbours(ag, net=self.Net):
            val = self.__foi(nei, model)
            nei.shock(ti, self.Name, self.Name, val)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Net
        return 'NetWeightShock({}, {} on {} of {})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        wt = kwargs['weight']
        wt = {model.DCore.States[k]: v for k, v in wt.items()}
        model.Behaviours[name] = NetWeightShock(name, s_src, t_tar, kwargs['net'], wt)


class SwitchOn(PassiveModBehaviour, metaclass=ABCMeta):
    def __init__(self, name, s_src, t_tar, prob):
        tri = StateTrigger(s_src)
        mod = BuffModifier(name, t_tar)
        PassiveModBehaviour.__init__(self, name, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Prob = prob
        self.Decision = 0
        self.Buff = 0

    def initialise(self, ti, model, *args, **kwargs):
        for ag in model.agents:
            if self.S_src in ag.State:
                self.__shock(ag, ti)

    def impulse_change(self, model, ag, ti):
        self.__shock(ag, ti)

    def impulse_enter(self, model, ag, ti):
        self.__shock(ag, ti)

    def impulse_exit(self, model, ag, ti):
        ag.shock(ti, self.Name, self.Name, False)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        model.Behaviours[name] = SwitchOn(name, s_src, t_tar, kwargs['prob'])

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
            ag.shock(ti, self.Name, self.Name, True)
            self.Buff += 1
        else:
            ag.shock(ti, self.Name, self.Name, False)


class SwitchOff(PassiveModBehaviour, metaclass=ABCMeta):
    def __init__(self, name, s_src, t_tar, prob):
        tri = StateTrigger(s_src)
        mod = NerfModifier(name, t_tar)
        PassiveModBehaviour.__init__(self, name, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Prob = prob
        self.Decision = 0
        self.Nerf = 0

    def initialise(self, ti, model, *args, **kwargs):
        for ag in model.agents:
            if self.S_src in ag.State:
                self.__shock(ag, ti)

    def impulse_change(self, model, ag, ti):
        self.__shock(ag, ti)

    def impulse_enter(self, model, ag, ti):
        self.__shock(ag, ti)

    def impulse_exit(self, model, ag, ti):
        ag.shock(ti, self.Name, self.Name, False)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        model.Behaviours[name] = SwitchOff(name, s_src, t_tar, kwargs['prob'])

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
            ag.shock(ti, self.Name, self.Name, True)
            self.Nerf += 1
        else:
            ag.shock(ti, self.Name, self.Name, False)
