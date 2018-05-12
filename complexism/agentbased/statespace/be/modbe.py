from complexism.element import Event, Clock
from ..modifier import GloRateModifier
from .behaviour import TimeIndModBehaviour, TimeDepModBehaviour
from .trigger import StateTrigger
__author__ = 'TimeWz667'
__all__ = ['FDShock', 'FDShockFast', 'DDShock', 'DDShockFast']


class FDShock(TimeIndModBehaviour):
    def __init__(self, name, s_src, t_tar):
        tri = StateTrigger(s_src)
        mod = GloRateModifier(name, t_tar)
        TimeIndModBehaviour.__init__(self, name, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Value = 0

    def initialise(self, model, ti):
        self.Value = model.Population.count(st=self.S_src) / len(model)
        self.__shock(model, ti)

    def impulse_change(self, model, ag, ti):
        self.Value = model.Population.count(st=self.S_src) / len(model)
        self.__shock(model, ti)

    def impulse_enter(self, model, ag, ti):
        self.Value += 1 / len(model)
        self.__shock(model, ti)

    def impulse_exit(self, model, ag, ti):
        self.Value -= 1 / len(model)
        self.__shock(model, ti)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        model.Behaviours[name] = FDShock(name, s_src, t_tar)

    def match(self, be_src, ags_src, ags_new, ti):
        self.Value = be_src.Value
        for ag in ags_new.values():
            self.register(ag, ti)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Value
        return 'FDShock({}, {} on {}, by={})'.format(*opt)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value

    def __shock(self, model, ti):
        self.ProtoModifier.Value = self.Value
        for ag in model.agents:
            ag.modify(self.Name, ti)


class FDShockFast(TimeDepModBehaviour):
    def __init__(self, name, s_src, t_tar, dt):
        mod = GloRateModifier(name, t_tar)
        TimeDepModBehaviour.__init__(self, name, Clock(dt=dt), mod)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Value = 0

    def initialise(self, time, *args, **kwargs):
        TimeDepModBehaviour.initialise(time, *args, **kwargs)
        model = kwargs['model']
        self.Value = model.Pop.count(self.S_src) / model.Pop.count()
        self.__shock(model, time)

    def reset(self, time, *args, **kwargs):
        self.Clock.initialise(time)
        model = kwargs['model']
        self.Value = model.Pop.count(self.S_src) / len(model)
        self.__shock(model, time)

    def compose_event(self, time):
        return Event(self.Name, time)

    def do_action(self, model, todo, time):
        self.__shock(model, time)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        dt = kwargs['dt'] if 'dt' in kwargs else 1
        model.Behaviours[name] = FDShockFast(name, s_src, t_tar, dt)

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
        return 'FDShockFast({}, {} on {}, by={})'.format(*opt)

    def __shock(self, model, ti):
        self.ProtoModifier.Value = self.Value
        for ag in model.agents:
            ag.modify(self.Name, ti)


class DDShock(TimeIndModBehaviour):
    def __init__(self, name, s_src, t_tar):
        tri = StateTrigger(s_src)
        mod = GloRateModifier(name, t_tar)
        TimeIndModBehaviour.__init__(self, name, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Value = 0

    def initialise(self, model, ti):
        self.Value = model.Population.count(st=self.S_src)
        self.__shock(model, ti)

    def impulse_change(self, model, ag, ti):
        self.Value = model.Population.count(st=self.S_src)
        self.__shock(model, ti)

    def impulse_enter(self, model, ag, ti):
        self.Value += 1
        self.__shock(model, ti)

    def impulse_exit(self, model, ag, ti):
        self.Value -= 1
        self.__shock(model, ti)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        model.Behaviours[name] = DDShock(name, s_src, t_tar)

    def match(self, be_src, ags_src, ags_new, ti):
        self.Value = be_src.Value
        for ag in ags_new.values():
            self.register(ag, ti)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Value
        return 'DDShock({}, {} on {}, by={})'.format(*opt)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value

    def __shock(self, model, ti):
        self.ProtoModifier.Value = self.Value
        for ag in model.agents:
            ag.modify(self.Name, ti)


class DDShockFast(TimeDepModBehaviour):
    def __init__(self, name, s_src, t_tar, dt):
        mod = GloRateModifier(name, t_tar)
        TimeDepModBehaviour.__init__(self, name, Clock(dt=dt), mod)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Value = 0

    def initialise(self, time, *args, **kwargs):
        TimeDepModBehaviour.initialise(time, *args, **kwargs)
        model = kwargs['model']
        self.Value = model.Pop.count(self.S_src) / model.Pop.count()
        self.__shock(model, time)

    def reset(self, time, *args, **kwargs):
        self.Clock.initialise(time)
        model = kwargs['model']
        self.Value = model.Pop.count(self.S_src) / len(model)
        self.__shock(model, time)

    def compose_event(self, time):
        return Event(self.Name, time)

    def do_action(self, model, todo, time):
        self.__shock(model, time)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        dt = kwargs['dt'] if 'dt' in kwargs else 1
        model.Behaviours[name] = DDShockFast(name, s_src, t_tar, dt)

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
        return 'DDShockFast({}, {} on {}, by={})'.format(*opt)

    def __shock(self, model, ti):
        self.ProtoModifier.Value = self.Value
        for ag in model.agents:
            ag.modify(self.Name, ti)
