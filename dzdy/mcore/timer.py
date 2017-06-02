__author__ = 'TimeWz667'


class Clock:
    def __init__(self, ini=0, last=0, by=1):
        self.Initial = ini
        self.Last = last
        self.By = by

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

    def __repr__(self):
        return 'Clock(T0={}, Now={}, Tick={})'.format(self.Initial, self.Last, self.By)


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
