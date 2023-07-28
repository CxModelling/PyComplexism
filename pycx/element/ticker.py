from abc import ABCMeta, abstractmethod
from sims_pars.factory import get_workshop
import sims_pars.factory.arguments as vld

__author__ = 'TimeWz667'
__all__ = ['AbsTicker', 'StepTicker', 'ScheduleTicker', 'AppointmentTicker']


class AbsTicker(metaclass=ABCMeta):
    def __init__(self, t=0):
        self.Last = t
        self.json = None

    def initialise(self, t):
        self.Last = t

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
        return {'Type': self.Type, 'Args': args}

    def __repr__(self):
        return str(self.to_json())


class StepTicker(AbsTicker):
    def __init__(self, dt):
        AbsTicker.__init__(self)
        self.Dt = dt

    def args(self):
        return {'dt': self.Dt}

    @property
    def Type(self):
        return 'Clock'

    @property
    def Next(self):
        return self.Last + self.Dt


class ScheduleTicker(AbsTicker):
    def __init__(self, ts):
        AbsTicker.__init__(self)
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
    def __init__(self, queue=None):
        AbsTicker.__init__(self)
        self.Queue = list(queue) if queue else list()

    def initialise(self, t):
        AbsTicker.initialise(self, t)
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


if __name__ == '__main__':
    clock = TickerLibrary.parse('Step(0.5)')
    clock.initialise(0)
    ti = clock.Next
    print(ti)
    while ti < 3:
        clock.update(ti)
        ti = clock.Next
        print(ti)

    print()
    clock = TickerLibrary.create('Schedule', ts=[0.5, 1.9])
    clock.initialise(0)
    ti = clock.Next
    print(ti)
    while ti < 3:
        clock.update(ti)
        ti = clock.Next
        print(ti)
    clock.update(3)

    print(clock.to_json())
