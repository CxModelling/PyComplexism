import numpy.random as rd
import numpy as np
import logging

__author__ = 'TimeWz667'
__all__ = ['Simulator']


class PseudoLogger:
    def info(self, msg):
        pass


class Simulator:
    def __init__(self, model, seed=None, keep_log=True, new_log=True):
        self.Model = model
        if seed:
            rd.seed(seed)
        self.Time = 0

        self.Models = dict()

        if keep_log:
            self.Logger = logging.getLogger(__name__)
            if new_log:
                file = '{}.log'.format(self.Model.Name)
                with open(file, 'w'):
                    pass
                self.Logger.setLevel(logging.INFO)
                fh = logging.FileHandler(file)
                fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
                self.Logger.addHandler(fh)
        else:
            self.Logger = PseudoLogger()

    def simulate(self, y0, fr, to, dt):
        self.Time = fr
        self.Model.set_observation_interval(dt)
        self.Model.initialise(ti=fr, y0=y0)
        self.deal_with_disclosures(fr, None)
        self.Model.initialise_observations(fr)
        self.Model.push_observations(fr)
        self.update(to, dt)

    def update(self, forward, dt):
        self.deal_with_disclosures(self.Time, None)
        num = int((forward - self.Time) / dt) + 1
        ts = list(np.linspace(self.Time, forward, num))
        if ts[-1] != forward:
            ts.append(forward)
        for f, t in zip(ts[:-1], ts[1:]):
            self.step(f, (f+t)/2)
            self.Model.capture_mid_term_observations(t)
            self.step((f+t)/2, t)
            self.Model.update_observations(t)
            self.Model.push_observations(t)

    def step(self, t, end):
        tx = t
        while tx < end:
            self.Model.collect_requests()
            requests = self.Model.Scheduler.Requests
            ti = self.Model.Scheduler.Time
            if ti > end:
                break
            tx = ti
            for req in requests:
                self.Logger.info(str(req))
            self.Model.fetch_requests(requests)
            self.Model.synchronise_request_time(ti)
            self.Model.execute_requests()
            self.deal_with_disclosures(ti, requests)
            self.Model.exit_cycle()
        self.Model.exit_cycle()
        # self.Model.print_schedule()
        self.Time = end
        self.Model.TimeEnd = end

    def deal_with_disclosures(self, time, requests):
        if requests:
            ds = [req.to_disclosure() for req in requests]
        else:
            ds = list()
        ds += self.Model.collect_disclosure()
        ds = [d for d in ds if d.Where[0] != self.Model.Name]
        for d in ds:
            self.Logger.info(str(d))

        while len(ds) > 0:
            ds_ms = [(d.down_scale()[1], self._find_model(d)) for d in ds]
            self.Model.fetch_disclosures(ds_ms, time)

            ds = self.Model.collect_disclosure()
            ds = [d for d in ds if d.Where[0] != self.Model.Name]
            for d in ds:
                self.Logger.info(str(d))

    def _find_model(self, dis):
        adr = dis.Address
        try:
            return self.Models[adr]
        except KeyError:
            where = dis.Where
            where = list(where[:-1])
            where.reverse()
            mod = self.Model
            for sel in where:
                mod = mod.get_model(sel)
            self.Models[adr] = mod
            return mod
