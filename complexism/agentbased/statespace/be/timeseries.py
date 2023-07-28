import scipy.interpolate as ipl
from abc import ABCMeta, abstractmethod
from element import Event, ScheduleTicker, StepTicker
from ..modifier import GloRateModifier
from .behaviour import ActiveModBehaviour

__author__ = 'TimeWz667'
__all__ = ['AbsTimeVarying',
           'TimeFunction', 'TimeSeriesInterp', 'TimeSeriesStep']


class AbsTimeVarying(ActiveModBehaviour, metaclass=ABCMeta):
    def __init__(self, clock, t_tar):
        mod = GloRateModifier(t_tar)
        ActiveModBehaviour.__init__(self, clock, mod)
        self.T_tar = t_tar
        self.Value = 1

    def initialise(self, ti, model):
        self._shock(model, ti)

    def reset(self, ti, model):
        self._shock(model, ti)

    def compose_event(self, ti):
        return Event('update value', self.Clock.Next)

    def do_action(self, model, td, ti):
        self._shock(model, ti)

    @abstractmethod
    def _find_value(self, ti):
        pass

    def _shock(self, model, ti):
        v0, self.Value = self.Value, self._find_value(ti)
        self.ProtoModifier.Value = self.Value
        for ag in model.agents:
            ag.modify(self.Name, ti)
        model.disclose('update value from {} to {}'.format(v0, self.Value),
                       self.Name, v0=v0, v1=self.Value)

    def match(self, be_src, ags_src, ags_new, ti):
        for ag in ags_new.values():
            self.register(ag, ti)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value


class TimeFunction(AbsTimeVarying):
    def __init__(self, t_tar, func, dt):
        AbsTimeVarying.__init__(self, StepTicker(dt), t_tar)
        self.Func = func

    def _find_value(self, ti):
        return self.Func(ti)

    def to_json(self):
        return {
            'Name': self.Name,
            'Type': 'TimeFunction',
            'Args': {
                't_tar': self.T_tar.Name,
                'dt': self.Clock.dt,
                'func': self.Func
            }
        }

    def to_data(self):
        return {
            self.Name: self.Value
        }


class TimeSeriesInterp(AbsTimeVarying):
    def __init__(self, t_tar, ts, ys):
        clock = ScheduleTicker(ts)
        AbsTimeVarying.__init__(self, clock, t_tar)
        self.Ts = ts
        self.Ys = ys
        self.Func = ipl.interp1d(ts, ys, bounds_error=False, fill_value=(ys[0], ys[-1]))

    def _find_value(self, ti):
        return self.Func(ti)

    @staticmethod
    def decorate(name, model, **kwargs):
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        ts = kwargs['ts']
        ys = kwargs['ys']
        model.add_behaviour(TimeSeriesInterp(t_tar, ts, ys))


class TimeSeriesStep(AbsTimeVarying):
    def __init__(self, t_tar, ts, ys):
        clock = ScheduleTicker(ts)
        AbsTimeVarying.__init__(self, clock, t_tar)
        self.Ts = ts
        self.Ys = ys

    def _find_value(self, ti):
        for i, t in enumerate(self.Ts):
            if t >= ti:
                return self.Ys[i]
        return float('inf')

    def __repr__(self):
        if len(self.Ys) <= 3:
            ys = ', '.join(self.Ys)
        else:
            ys = ', '.join(self.Ys[:3])

        ys = '[' + ys + ']'
        opt = self.Name, ys
        return '{}({})'.format(*opt)
