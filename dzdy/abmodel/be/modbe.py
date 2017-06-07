from dzdy.abmodel.behaviour import *
from dzdy.abmodel.trigger import *
from dzdy.abmodel.modifier import *
import numpy.random as rd

__author__ = 'TimeWz667'


class ComFDShock(ModBe):
    def __init__(self, name, s_src, t_tar):
        tri = StateTrigger(s_src)
        mod = GloRateModifier(name, t_tar)
        ModBe.__init__(self, name, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Val = 0

    def initialise(self, model, ti):
        self.Val = model.Pop.count(self.S_src)/model.Pop.count()
        self.shock(model, ti)

    def impulse_tr(self, model, ag, ti):
        self.Val = model.Pop.count(self.S_src)/model.Pop.count()
        self.shock(model, ti)

    def impulse_in(self, model, ag, ti):
        self.Val += 1/model.Pop.count()
        self.shock(model, ti)

    def impulse_out(self, model, ag, ti):
        self.Val -= 1/model.Pop.count()
        self.shock(model, ti)

    def shock(self, model, ti):
        self.ModPrototype.Val = self.Val
        for ag in model.agents:
            ag.modify(self.Name, ti)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Val
        return 'FDShock({}, {} on {}, by={})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        model.Behaviours[name] = ComFDShock(name, s_src, t_tar)

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.Val


class ComFDShockFast(TimeModBe):
    def __init__(self, name, s_src, t_tar, dt):
        mod = GloRateModifier(name, t_tar)
        TimeModBe.__init__(self, name, Clock(by=dt), mod)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Val = 0

    def initialise(self, model, ti):
        self.Clock.initialise(ti)
        self.Val = model.Pop.count(self.S_src)/model.Pop.count()
        self.shock(model, ti)

    def shock(self, model, ti):
        self.ModPrototype.Val = self.Val = model.Pop.count(self.S_src)/model.Pop.count()
        for ag in model.agents:
            ag.modify(self.Name, ti)

    def do_request(self, model, evt, ti):
        self.shock(model, evt.Time)

    def compose_event(self, ti):
        return Event(self.Name, ti)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Val
        return 'FDShock({}, {} on {}, by={})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        dt = kwargs['dt'] if 'dt' in kwargs else 1
        model.Behaviours[name] = ComFDShockFast(name, s_src, t_tar, dt)

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.Val


class ComDDShock(ModBe):
    def __init__(self, name, s_src, t_tar):
        tri = StateTrigger(s_src)
        mod = GloRateModifier(name, t_tar)
        ModBe.__init__(self, name, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Val = 0

    def initialise(self, model, ti):
        self.Val = model.Pop.count(self.S_src)
        self.shock(model, ti)

    def impulse_tr(self, model, ag, ti):
        self.Val = model.Pop.count(self.S_src)
        self.shock(model, ti)

    def impulse_in(self, model, ag, ti):
        self.Val += 1
        self.shock(model, ti)

    def impulse_out(self, model, ag, ti):
        self.Val -= 1
        self.shock(model, ti)

    def shock(self, model, ti):
        self.ModPrototype.Val = self.Val
        for ag in model.agents:
            ag.modify(self.Name, ti)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Val
        return 'DDShock({}, {} on {}, by={})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        model.Behaviours[name] = ComDDShock(name, s_src, t_tar)

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.Val


class ComDDShockFast(TimeModBe):
    def __init__(self, name, s_src, t_tar, dt):
        mod = GloRateModifier(name, t_tar)
        TimeModBe.__init__(self, name, Clock(by=dt), mod)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Val = 0

    def initialise(self, model, ti):
        self.Clock.initialise(ti)
        self.Val = model.Pop.count(self.S_src)
        self.shock(model, ti)

    def shock(self, model, ti):
        self.ModPrototype.Val = self.Val = model.Pop.count(self.S_src)
        for ag in model.agents:
            ag.modify(self.Name, ti)

    def do_request(self, model, evt, ti):
        self.shock(model, evt.Time)

    def compose_event(self, ti):
        return Event(self.Name, ti)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Val
        return 'DDShock({}, {} on {}, by={})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        dt = kwargs['dt'] if 'dt' in kwargs else 1
        model.Behaviours[name] = ComDDShockFast(name, s_src, t_tar, dt)

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.Val


class ComWeightSumShock(TimeModBe):
    def __init__(self, name, s_src, t_tar, weight, dt):
        mod = GloRateModifier(name, t_tar)
        TimeModBe.__init__(self, name, Clock(by=dt), mod)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Weight = weight
        self.Val = 0

    def initialise(self, model, ti):
        self.Clock.initialise(ti)
        self.shock(model, ti)

    def shock(self, model, ti):
        self.Val = [model.Pop.count(k)*v for k, v in self.Weight.items()]
        self.Val = sum(self.Val)
        self.ModPrototype.Val = self.Val
        for ag in model.agents:
            ag.modify(self.Name, ti)

    def do_request(self, model, evt, ti):
        self.shock(model, evt.Time)

    def compose_event(self, ti):
        return Event(self.Name, ti)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Val
        return 'WeightSumShock({}, {} on {}, by={})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        dt = kwargs['dt'] if 'dt' in kwargs else 1
        wt = kwargs['weight']
        wt = {model.DCore.States[k]: v for k, v in wt.items()}
        model.Behaviours[name] = ComWeightSumShock(name, s_src, t_tar, wt, dt)

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.Val


class ComWeightAvgShock(TimeModBe):
    def __init__(self, name, s_src, t_tar, weight, dt):
        mod = GloRateModifier(name, t_tar)
        TimeModBe.__init__(self, name, Clock(by=dt), mod)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Weight = weight
        self.Val = 0

    def initialise(self, model, ti):
        self.Clock.initialise(ti)
        self.shock(model, ti)

    def shock(self, model, ti):
        self.Val = [model.Pop.count(k)*v for k, v in self.Weight.items()]
        self.Val = sum(self.Val)/model.Pop.count()
        self.ModPrototype.Val = self.Val
        for ag in model.agents:
            ag.modify(self.Name, ti)

    def do_request(self, model, evt, ti):
        self.shock(model, evt.Time)

    def compose_event(self, ti):
        return Event(self.Name, ti)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Val
        return 'WeightAvgShock({}, {} on {}, by={})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        dt = kwargs['dt'] if 'dt' in kwargs else 1
        wt = kwargs['weight']
        wt = {model.DCore.States[k]: v for k, v in wt.items()}
        model.Behaviours[name] = ComWeightAvgShock(name, s_src, t_tar, wt, dt)

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.Val


class NetShock(ModBe):
    def __init__(self, name, s_src, t_tar, net):
        tri = StateTrigger(s_src)
        mod = LocRateModifier(name, t_tar)
        ModBe.__init__(self, name, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Net = net
        self.Val = 0

    def initialise(self, model, ti):
        for ag in model.agents:
            val = model.Pop.count_neighbours(ag, self.S_src, net=self.Net)
            ag.shock(self.Name, val, ti)

    def impulse_tr(self, model, ag, ti):
        self.shock(ag, model, ti)

    def impulse_in(self, model, ag, ti):
        self.shock(ag, model, ti)

    def impulse_out(self, model, ag, ti):
        self.shock(ag, model, ti)

    def shock(self, ag, model, ti):
        val = model.Pop.count_neighbours(ag, self.S_src, net=self.Net)
        ag.shock(self.Name, val, ti)
        for nei in model.Pop.neighbours(ag, net=self.Net):
            val = model.Pop.count_neighbours(nei, self.S_src, net=self.Net)
            nei.shock(self.Name, val, ti)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Net, self.Val
        return 'NetShock({}, {} on {} of {}, FOI={})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        model.Behaviours[name] = NetShock(name, s_src, t_tar, kwargs['net'])

    def fill(self, obs, model, ti):
        return obs


class NetWeightShock(ModBe):
    def __init__(self, name, s_src, t_tar, net, weight):
        tri = StateTrigger(s_src)
        mod = LocRateModifier(name, t_tar)
        ModBe.__init__(self, name, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Net = net
        self.Weight = weight
        self.Val = 0

    def initialise(self, model, ti):
        for ag in model.agents:
            val = sum([model.Pop.count_neighbours(ag, st=k, net=self.Net)*v for k, v in self.Weight.items()])
            ag.shock(self.Name, val, ti)

    def impulse_tr(self, model, ag, ti):
        self.shock(ag, model, ti)

    def impulse_in(self, model, ag, ti):
        self.shock(ag, model, ti)

    def impulse_out(self, model, ag, ti):
        self.shock(ag, model, ti)

    def shock(self, ag, model, ti):
        val = sum([model.Pop.count_neighbours(ag, st=k, net=self.Net)*v for k, v in self.Weight.items()])
        ag.shock(self.Name, val, ti)
        for nei in model.Pop.neighbours(ag, net=self.Net):
            val = sum([model.Pop.count_neighbours(nei, st=k, net=self.Net) * v for k, v in self.Weight.items()])
            nei.shock(self.Name, val, ti)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Net, self.Val
        return 'NetShock({}, {} on {} of {}, FOI={})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        wt = kwargs['weight']
        wt = {model.DCore.States[k]: v for k, v in wt.items()}
        model.Behaviours[name] = NetWeightShock(name, s_src, t_tar, kwargs['net'], wt)

    def fill(self, obs, model, ti):
        return obs


class NerfDecision(ModBe):
    def __init__(self, name, s_src, t_tar, prob):
        tri = StateTrigger(s_src)
        mod = NerfModifier(name, t_tar)
        ModBe.__init__(self, name, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Prob = prob
        self.Decision = 0
        self.Nerf = 0

    def initialise(self, model, ti):
        for ag in model.agents:
            if self.S_src in ag.State:
                self.shock(ag, ti)

    def impulse_tr(self, model, ag, ti):
        self.shock(ag, ti)

    def impulse_in(self, model, ag, ti):
        self.shock(ag, ti)

    def impulse_out(self, model, ag, ti):
        ag.shock(self.Name, False, ti)

    def shock(self, ag, ti):
        self.Decision += 1
        if rd.random() < self.Prob:
            ag.shock(self.Name, True, ti)
            self.Nerf += 1
        else:
            ag.shock(self.Name, False, ti)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Nerf/self.Decision
        return 'Nerf({}, {} on {}, Prob={})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        model.Behaviours[name] = NerfDecision(name, s_src, t_tar, kwargs['p'])

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.Nerf/self.Decision


class BuffDecision(ModBe):
    def __init__(self, name, s_src, t_tar, prob):
        tri = StateTrigger(s_src)
        mod = BuffModifier(name, t_tar)
        ModBe.__init__(self, name, mod, tri)
        self.S_src = s_src
        self.T_tar = t_tar
        self.Prob = prob
        self.Decision = 0
        self.Buff = 0

    def initialise(self, model, ti):
        for ag in model.agents:
            if self.S_src in ag.State:
                self.shock(ag, ti)

    def impulse_tr(self, model, ag, ti):
        self.shock(ag, ti)

    def impulse_in(self, model, ag, ti):
        self.shock(ag, ti)

    def impulse_out(self, model, ag, ti):
        ag.shock(self.Name, False, ti)

    def shock(self, ag, ti):
        self.Decision += 1

        if rd.random() < self.Prob:
            ag.shock(self.Name, True, ti)
            self.Buff += 1
        else:
            ag.shock(self.Name, False, ti)

    def __repr__(self):
        opt = self.Name, self.S_src.Name, self.T_tar.Name, self.Buff/self.Decision
        return 'Buff({}, {} on {}, Prob={})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        model.Behaviours[name] = BuffDecision(name, s_src, t_tar, kwargs['p'])

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.Buff/self.Decision


class ForeignShock(ModBe):
    def __init__(self, name, src_model, src_value, src_target):
        tri = ForeignTrigger(src_model, src_value)
        mod = GloRateModifier(name, src_target)
        ModBe.__init__(self, name, mod, tri)
        self.Source = src_model, src_value
        self.Target = src_target.Name
        self.Val = 0

    def initialise(self, model, ti):
        self.shock(model, ti)

    def impulse_foreign(self, model, fore, ti):
        self.Val = fore[self.Source[1]]/100
        self.shock(model, ti)

    def shock(self, model, ti):
        self.ModPrototype.Val = self.Val
        for ag in model.agents:
            ag.modify(self.Name, ti)

    def __repr__(self):
        opt = self.Name, '{}:{}'.format(*self.Source), self.Target, self.Val
        return 'Foreign({}, {} on {}, Value={})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        target = model.DCore.Transitions[kwargs['src_target']]
        model.Behaviours[name] = ForeignShock(name, kwargs['src_model'], kwargs['src_value'], target)

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.Val
        return obs
