from abc import ABCMeta, abstractmethod
from factory.manager import getWorkshop
import factory.arguments as vld

__author__ = 'TimeWz667'
__all__ = ['Clock', 'AbsTicker', 'ClockTicker', 'StepTicker', 'AppointmentTicker']


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
        while now > self.Last:
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


class ClockTicker(AbsTicker):
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
    return ClockTicker('', dt)


class StepTicker(AbsTicker):
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
    def __init__(self, name, queue, t=0):
        AbsTicker.__init__(self, name)
        self.initialise(t)
        self.Queue = set(queue)
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


TickerLibrary = getWorkshop('Ticker')
TickerLibrary.register('Clock', ClockTicker, [vld.Prob('dt')])
TickerLibrary.register('Step', StepTicker, [vld.List('ts')])
TickerLibrary.register('Appointment', AppointmentTicker, [vld.List('queue')])


if __name__ == '__main__':
    def try_ticker(ticker, tend):
        print('Before test')
        print(ticker.to_json())
        print('Start')
        ticker.initialise(0)
        ti = ticker.Next
        while ti < tend:
            print(ti)
            ticker.update(ti)
            ti = ticker.Next
        print(ti)
        print('After test')
        print(ticker.to_json())

    tk = TickerLibrary.from_json({'Name': '', 'Type': 'Clock', 'Args': {'dt': 0.5}})
    try_ticker(tk, 2)

    tk = TickerLibrary.from_json({'Name': '', 'Type': 'Step',
                                  'Args': {'ts': [0.4, 0.6, 1.5]}})
    try_ticker(tk, 2)

    tk = TickerLibrary.from_json({'Name': '', 'Type': 'Appointment',
                                  'Args': {'queue': [-5, 0.4, 0.6]}})
    tk.make_an_appointment(1.5)
    try_ticker(tk, 2)
