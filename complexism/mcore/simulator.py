from complexism.element import Schedule
import numpy.random as rd
import numpy as np

__author__ = 'TimeWz667'


class Simulator:
    def __init__(self, model, seed=None):
        self.Model = model
        if seed:
            rd.seed(seed)
        self.Time = 0
        self.Receptor = Schedule()

    def simulate(self, y0, fr, to, dt):
        self.Time = fr
        self.Model.initialise(ti=fr, y0=y0)
        self.Model.initialise_observations(fr)
        self.Model.push_observations(fr)
        self.update(to, dt)

    def update(self, forward, dt):
        num = int((forward - self.Time) / dt) + 1
        ts = list(np.linspace(self.Time, forward, num))
        if ts[-1] != forward:
            ts.append(forward)
        for f, t in zip(ts[:-1], ts[1:]):
            self.step(f, (f+t)/2)
            self.Model.captureMidTermObservations(t)
            self.step((f+t)/2, t)
            self.Model.update_observations(t)
            self.Model.push_observations(t)

    def step(self, t, end):
        tx = t
        self.Model.drop_next()
        self.Receptor.clear()
        while tx < end:
            self.Receptor.append_requests(self.Model.Next)

            ti = self.Receptor.Time
            if ti > end:
                break
            tx = ti
            rqs = self.Receptor.RequestSet
            self.Model.fetch_requests(rqs)
            self.Model.execute_requests()
            self.Model.drop_next()
            self.Receptor.clear()

        self.Time = end
        self.Model.TimeEnd = end
