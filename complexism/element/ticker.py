from abc import ABCMeta, abstractmethod
from epidag.factory import get_workshop
import epidag.factory.arguments as vld

__author__ = 'TimeWz667'
__all__ = ['Clock', 'AbsTicker', 'StepTicker', 'ScheduleTicker', 'AppointmentTicker']


class AbsTicker(metaclass=ABCMeta):
    def __init__(self, name, t=0):
        self.Name = name
        self.Last = t

    def initialise(self, ti):
        self.Last = ti

    @property
    @abstractmethod
    def Next(self):
        pass

    def update(self, now):
        while now >= self.Next:
            self.Last = self.Next

    @property
    @abstractmethod
    def Type(self):
        pass

    @abstractmethod
    def args(self):
        pass

    def to_json(self):
        args = self.args()
        args['t'] = self.Last
        return {'Name': self.Name, 'Type': self.Type, 'Args': args}

    def __repr__(self):
        return str(self.to_json())


class StepTicker(AbsTicker):
    def __init__(self, name, dt, t=0):
        AbsTicker.__init__(self, name)
        self.initialise(t)
        self.Dt = dt

    def args(self):
        return {'dt': self.Dt}

    @property
    def Type(self):
        return 'Clock'

    @property
    def Next(self):
        return self.Last + self.Dt


def Clock(dt):
    return StepTicker('', dt)


class ScheduleTicker(AbsTicker):
    def __init__(self, name, ts, t=0):
        AbsTicker.__init__(self, name)
        self.initialise(t)
        self.TS = ts

    def args(self):
        return {'ts': self.TS}

    @property
    def Type(self):
        return 'Step'

    @property
    def Next(self):
        for t in self.TS:
            if t > self.Last:
                return t
        return float('inf')


class AppointmentTicker(AbsTicker):
    def __init__(self, name, queue=None, t=0):
        AbsTicker.__init__(self, name)
        self.initialise(t)
        self.Queue = set(queue) if queue else set()
        self.Queue = [q for q in self.Queue if q >= t]
        self.Queue.sort()

    def make_an_appointment(self, ap):
        if ap >= self.Last:
            self.Queue.append(ap)
            self.Queue.sort()

    def update(self, now):
        AbsTicker.update(self, now)
        self.Queue = [q for q in self.Queue if q > now]

    def args(self):
        return {'queue': self.Queue}

    @property
    def Type(self):
        return 'Appointment'

    @property
    def Next(self):
        for t in self.Queue:
            if t > self.Last:
                return t
        return float('inf')


TickerLibrary = get_workshop('Ticker')
TickerLibrary.register('Step', StepTicker, [vld.Prob('dt')])
TickerLibrary.register('Schedule', ScheduleTicker, [vld.List('ts')])
TickerLibrary.register('Appointment', AppointmentTicker, [vld.List('queue')])
