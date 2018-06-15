from abc import ABCMeta, abstractmethod
from complexism.element import Event, Schedule
from complexism.mcore import ModelSelector


class AbsModel(metaclass=ABCMeta):
    def __init__(self, name, env=None):
        self.Name = name
        self.Scheduler = Schedule(self.Name)
        self.Validator = None
        self.Environment = env
        self.TimeEnd = None

    @abstractmethod
    def collect_requests(self):
        pass

    @abstractmethod
    def find_next(self):
        pass

    def request(self, event, who):
        self.Scheduler.append_request_from_source(event, who)

    @abstractmethod
    def do_request(self, request):
        pass

    @abstractmethod
    def validate_requests(self):
        pass

    @abstractmethod
    def fetch_requests(self, requests):
        pass

    @abstractmethod
    def execute_requests(self):
        pass

    def disclose(self, msg, who):
        self.Scheduler.append_disclosure_from_source(msg, who)

    @abstractmethod
    def collect_disclosure(self):
        pass

    @abstractmethod
    def fetch_disclosures(self, ds_ms, time):
        pass

    @abstractmethod
    def trigger_external_impulses(self, disclosure, model, time):
        pass

    def exit_cycle(self):
        if not self.Scheduler.waiting_for_validation():
            self.Scheduler.cycle_completed()

    @abstractmethod
    def print_schedule(self):
        pass


class LeafModel(AbsModel, metaclass=ABCMeta):
    def __init__(self, name, env):
        AbsModel.__init__(self, name, env)

    def collect_requests(self):
        if self.Scheduler.waiting_for_collection():
            self.find_next()
            self.Scheduler.collection_completed()
            return self.Scheduler.Requests
        elif self.Scheduler.waiting_for_validation():
            return self.Scheduler.Requests
        else:
            raise AttributeError(self.Scheduler.Status)

    def validate_requests(self):
        # todo validation if not validated, disapprove
        pass

    def fetch_requests(self, rs):
        self.Scheduler.fetch_requests(rs)
        self.Scheduler.validation_completed()

    def execute_requests(self):
        if self.Scheduler.waiting_for_execution():
            for request in self.Scheduler.Requests:
                self.do_request(request)
            self.Scheduler.execution_completed()

    def collect_disclosure(self):
        return self.Scheduler.pop_disclosures()

    def fetch_disclosures(self, ds_ms, time):
        for d, m in ds_ms:
            self.trigger_external_impulses(d, m, time)
        #if not self.Scheduler.Disclosures:
        #    self.Scheduler.cycle_completed()

    def print_schedule(self):
        self.Scheduler.print()


class BranchModel(AbsModel, metaclass=ABCMeta):
    def __init__(self, name, env=None):
        AbsModel.__init__(self, name, env)

    @abstractmethod
    def all_models(self)->dict:
        pass

    @abstractmethod
    def get_model(self, k):
        pass

    def select(self, mod):
        return self.get_model(mod)

    def select_all(self, sel):
        return ModelSelector(self.all_models()).select_all(sel)

    def collect_requests(self):
        if self.Scheduler.waiting_for_collection():
            self.find_next()
            for v in self.all_models().values():
                v.collect_requests()
                self.Scheduler.append_lower_schedule(v.Scheduler)
            self.Scheduler.collection_completed()
        return self.Scheduler.Requests

    def validate_requests(self):
        pass  # todo

    def fetch_requests(self, rs):
        self.Scheduler.fetch_requests(rs)

        res = self.Scheduler.pop_lower_requests()

        for k, v in res.items():
            self.select(k).fetch_requests(v)
        if res or self.Scheduler.Requests:
            self.Scheduler.validation_completed()

    def execute_requests(self):
        for v in self.all_models().values():
            v.execute_requests()

        if self.Scheduler.waiting_for_execution():
            for request in self.Scheduler.Requests:
                self.do_request(request)
            self.Scheduler.execution_completed()

    def collect_disclosure(self):
        dss = self.Scheduler.pop_disclosures()
        for v in self.all_models().values():
            ds = v.collect_disclosure()
            ds = [d.up_scale(self.Name) for d in ds]
            dss += ds
        return dss

    def fetch_disclosures(self, ds_ms, time):
        for d, m in ds_ms:
            self.trigger_external_impulses(d, m, time)
        if not self.Scheduler.Disclosures:
            self.Scheduler.cycle_completed()

        for k, mod in self.all_models().items():
            ds = list()
            for d, fore in ds_ms:
                if d.Group == k:
                    if d.Where[0] != k:
                        ds.append((d.down_scale()[1], fore))
                else:
                    ds.append((d.sibling_scale(), fore))
            if ds:
                mod.fetch_disclosures(ds, time)

    @abstractmethod
    def do_request(self, request):
        pass

    def exit_cycle(self):
        for v in self.all_models().values():
            v.exit_cycle()
        AbsModel.exit_cycle(self)

    def print_schedule(self):
        self.Scheduler.print()
        for m in self.all_models().values():
            m.print_schedule()


class Country(BranchModel):
    def __init__(self, name):
        BranchModel.__init__(self, name)
        self.Models = dict()
        self.Check = False

    def all_models(self) -> dict:
        return self.Models

    def get_model(self, k):
        return self.Models[k]

    def do_request(self, request):
        self.Check = True
        self.disclose(request.Message, request.When)

    def find_next(self):
        if not self.Check:
            self.request(Event('Country', 5), 'self')

    def trigger_external_impulses(self, disclosure, model, time):
        # print(self.Name, disclosure, time)
        pass


class City(BranchModel):
    def __init__(self, name):
        BranchModel.__init__(self, name)
        self.Models = dict()
        self.Check = False

    def all_models(self) -> dict:
        return self.Models

    def get_model(self, k):
        return self.Models[k]

    def do_request(self, request):
        self.Check = True
        self.disclose(request.Message, request.When)

    def find_next(self):
        if not self.Check:
            self.request(Event('broadcast', 3), 'self')

    def trigger_external_impulses(self, disclosure, model, ti):
        # print(self.Name, disclosure, time)
        pass


import numpy.random as rd
import numpy as np


class School(LeafModel):
    def __init__(self, name):
        LeafModel.__init__(self, name, None)
        self.Last = 0

    def find_next(self):
        self.request(Event(self.Name, self.Last+rd.random()*5), 'student')

    def do_request(self, request):
        self.disclose("teach", self.Name)
        self.Last = request.When

    def trigger_external_impulses(self, disclosure, model, time):
        # print(self.Name, disclosure, time)
        pass


class Simulator:
    def __init__(self, model, seed=None):
        self.Model = model
        if seed:
            rd.seed(seed)
        self.Time = 0

    def simulate(self, y0, fr, to, dt):
        self.Time = fr
        # self.Model.initialise(ti=fr, y0=y0)
        # self.Model.initialise_observations(fr)
        # self.Model.push_observations(fr)
        self.deal_with_disclosures(fr)
        self.update(to, dt)

    def update(self, forward, dt):
        num = int((forward - self.Time) / dt) + 1
        ts = list(np.linspace(self.Time, forward, num))
        if ts[-1] != forward:
            ts.append(forward)
        for f, t in zip(ts[:-1], ts[1:]):
            self.step(f, (f+t)/2)
            # self.Model.captureMidTermObservations(t)
            self.step((f+t)/2, t)
            # self.Model.update_observations(t)
            # self.Model.push_observations(t)

    def step(self, t, end):
        tx = t
        while tx < end:
            self.Model.collect_requests()
            req = self.Model.Scheduler.Requests
            ti = req[0].When
            if ti > end:
                break
            tx = ti

            self.Model.fetch_requests(req)
            self.Model.execute_requests()
            self.deal_with_disclosures(ti)
            self.Model.exit_cycle()
        self.Model.exit_cycle()
        # self.Model.print_schedule()
        print(end)
        self.Time = end
        self.Model.TimeEnd = end

    def deal_with_disclosures(self, time):
        while True:
            ds = self.Model.collect_disclosure()
            ds = [d for d in ds if d.Where[0] != self.Model.Name]

            if not ds:
                break
            ds_ms = [(d.down_scale()[1], self._find_model(d.Where)) for d in ds]
            print(ds)
            self.Model.fetch_disclosures(ds_ms, time)

    def _find_model(self, where):
        where = list(where[:-1])
        where.reverse()
        mod = self.Model
        for sel in where:
            mod = mod.get_model(sel)
        return mod


if __name__ == '__main__':

    tw = Country('Taiwan')
    tp = City('Taipei')
    tw.Models['Taipei'] = tp

    tn = City('Tainan')
    tw.Models['Tainan'] = tn

    for st in range(2):
        n = 'S{}'.format(st)
        tp.Models[n] = School(n)

    for st in range(2):
        n = 'S{}'.format(st)
        tn.Models[n] = School(n)

    s = Simulator(tw)
    s.simulate(None, 0, 10, 1)
