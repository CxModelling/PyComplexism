from dzdy.abmodel import TimeModBe, GloRateModifier, Clock, Event
import numpy as np
from scipy import interpolate

__author__ = 'TimeWz667'

__all__ = ['TimeVarying', 'TimeVaryingInterp']


class TimeVaryingInterp(TimeModBe):
    def __init__(self, name, ts, y, t_tar, dt):
        mod = GloRateModifier(name, t_tar)
        TimeModBe.__init__(self, name, Clock(by=dt), mod)
        self.Ts = ts
        self.Y = y
        self.Func = interpolate.interp1d(ts, y, bounds_error=False, fill_value=(y[0], y[-1]))
        self.Transition = t_tar
        self.Val = 0

    def initialise(self, model, ti):
        self.Clock.initialise(ti)
        self.shock(model, ti)

    def shock(self, model, ti):
        self.ModPrototype.Val = self.Val = self.Func(ti)
        for ag in model.agents:
            ag.modify(self.Name, ti)

    def do_request(self, model, evt, ti):
        self.shock(model, evt.Time)

    def compose_event(self, ti):
        if ti < self.Ts[0]:
            return Event(self.Name, self.Ts[0])
        if ti > self.Ts[-1]:
            return Event.NullEvent
        return Event(self.Name, ti)

    def __repr__(self):
        opt = self.Name, self.Transition.Name, self.Val
        return 'F(t)({} on {}, by {})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        tr = model.DCore.Transitions[kwargs['t_tar']]
        y = kwargs['y']
        dt = kwargs['dt'] if 'dt' in kwargs else np.diff(y).min()
        dt = dt if dt > 0 else 1
        model.Behaviours[name] = TimeVaryingInterp(name, kwargs['ts'], y, tr, dt)

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = float(self.Val)

    def match(self, be_src, ags_src, ags_new, ti):
        self.Val = be_src.Val
        for ag in ags_new.values():
            self.register(ag, ti)


class TimeVarying(TimeModBe):
    def __init__(self, name, func, t_tar, dt):
        mod = GloRateModifier(name, t_tar)
        TimeModBe.__init__(self, name, Clock(by=dt), mod)
        self.Func = func
        self.Transition = t_tar
        self.Val = 0

    def initialise(self, model, ti):
        self.Clock.initialise(ti)
        self.shock(model, ti)

    def shock(self, model, ti):
        self.ModPrototype.Val = self.Val = self.Func(ti)
        for ag in model.agents:
            ag.modify(self.Name, ti)

    def do_request(self, model, evt, ti):
        self.shock(model, evt.Time)

    def compose_event(self, ti):
        return Event(self.Name, ti)

    def __repr__(self):
        opt = self.Name, self.Transition.Name, self.Val
        return 'F(t)({} on {}, by {})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        tr = model.DCore.Transitions[kwargs['t_tar']]
        dt = kwargs['dt'] if 'dt' in kwargs else 1
        model.Behaviours[name] = TimeVarying(name, kwargs['func'], tr, dt)

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.Val

    def match(self, be_src, ags_src, ags_new, ti):
        for ag in ags_new.values():
            self.register(ag, ti)
