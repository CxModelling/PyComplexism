__author__ = 'TimeWz667'


class Clock:
    def __init__(self, ini=0, last=0, dt=1):
        self.Initial = ini
        self.Last = last
        self.By = dt

    def initialise(self, ti, t0=None):
        if t0:
            self.Initial = t0
        self.Last = self.Initial
        self.update(ti)

    def get_next(self):
        return self.Last + self.By

    def update(self, now):
        while now > self.Last:
            self.Last = self.get_next()

    def to_json(self):
        return {
            "Name": "Clock",
            "Type": "TimeTicker",
            'Args': {'dt': self.By}
        }

    def __repr__(self):
        return 'Clock(T0={}, Now={}, Tick={})'.format(self.Initial, self.Last, self.By)


class ClockStep:
    def __init__(self, ts):
        self.TS = ts
        self.Current = None
        self.Next = None

    def initialise(self, ti, t0=None):
        self.Current = -1
        self.Next = self.TS[0]
        self.update(ti)

    def get_next(self):
        return self.Next

    def update(self, now):
        while now >= self.Next:
            self.Current += 1
            try:
                self.Next = self.TS[self.Current+1]
            except IndexError:
                self.Next = float('inf')

    def __repr__(self):
        return 'Step(TS={})'.format(self.TS)


class Timer:
    def __init__(self, fr=0, every=1):
        self.Index = fr
        self.Every = every

    def tick(self):
        self.Index += 1
        if self.Index >= self.Every:
            self.Index = 0
            return True
        else:
            return False
