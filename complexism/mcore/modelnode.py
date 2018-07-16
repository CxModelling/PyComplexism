from abc import ABCMeta, abstractmethod
from complexism.element import Event, Schedule
from complexism.mcore import Observer, DefaultObserver, ModelSelector, EventListenerSet
from complexism.misc.counter import count

__author__ = 'TimeWz667'


__all__ = ['ModelAtom', 'LeafModel', 'BranchModel']


class ModelAtom(metaclass=ABCMeta):
    def __init__(self, name, pars=None):
        self.Name = name
        self.Parameters = pars
        self.Attributes = dict()
        self.__next = Event.NullEvent

    def __getitem__(self, item):
        try:
            return self.Parameters[item]
        except (KeyError, AttributeError, TypeError):
            pass

        try:
            return self.Attributes[item]
        except KeyError as e:
            raise e

    def __setitem__(self, key, value):
        self.Attributes[key] = value

    @property
    def Next(self):
        if self.__next is Event.NullEvent:
            self.__next = self.find_next()
        return self.__next

    @property
    def TTE(self):
        """
        Time to the next event
        :return: time to the next event
        :rtype: float
        """
        return self.__next.Time

    @abstractmethod
    def find_next(self):
        """
        Find the next event and assign it to self.__next
        :return: next event
        :rtype: Event
        """
        pass

    def drop_next(self):
        """
        Drop the next event and reset it to the null event
        """
        self.__next = Event.NullEvent

    def approve_event(self, evt):
        """
        Approve an event to the particle
        :param evt: event to be executed
        :type evt: Event
        """
        self.__next = evt

    @abstractmethod
    def execute_event(self):
        """
        Let the next event happen
        """
        pass

    def disapprove_event(self, ti):
        """
        Disapprove an event and update to time ti
        :param ti: update to ti without any event happened
        """
        self.update_time(ti)

    def update_time(self, ti):
        """
        Update to time to
        :param ti: time
        """
        pass

    @abstractmethod
    def initialise(self, ti, model, *args, **kwargs):
        pass

    @abstractmethod
    def reset(self, ti, model, *args, **kwargs):
        pass

    def shock(self, ti, source, target, value):
        pass

    def is_compatible(self, **kwargs):
        for k, v in kwargs.items():
            if self.Attributes[k] != v:
                return False
        return True

    def __lt__(self, other):
        return self.Name < other.Name

    def to_json(self):
        js = dict()
        js['Name'] = self.Name
        js['Attributes'] = dict(self.Attributes)
        return js

    def to_snapshot(self):
        return self.to_json()

    def __repr__(self):
        s = 'ID: {}'.format(self.Name)
        if self.Attributes:
            atr = ', '.join(['{}: {}'.format(k, v) for k, v in self.Attributes.items()])
            return '{}, {}'.format(s, atr)
        else:
            return s

    def to_data(self):
        dat = dict()
        dat['Name'] = self.Name
        dat.update(self.Attributes)
        return dat

    def clone(self, *args, **kwargs):
        self.__class__.__init__(self, self.Name, self.Parameters)


class AbsModel(metaclass=ABCMeta):
    def __init__(self, name, env=None, obs: Observer=None, y0_class=None):
        self.Name = name
        self.Observer = obs if obs else DefaultObserver()
        self.ClassY0 = y0_class
        self.Scheduler = Schedule(self.Name)
        self.Validator = None
        self.Listeners = EventListenerSet()
        self.Environment = env
        self.TimeEnd = None

    def __getitem__(self, item):
        try:
            return self.Environment[item]
        except KeyError as e:
            raise e

    def initialise(self, ti=None, y0=None):
        if y0:
            if self.ClassY0:
                y0 = y0 if isinstance(y0, self.ClassY0) else self.ClassY0.from_source(y0)
                y0.match_model(self)
            self.read_y0(y0, ti)
        self.preset(ti)

    def preset(self, ti):
        self.reset(ti)

    @abstractmethod
    def reset(self, ti):
        self.Scheduler.reschedule_all_actors(ti)

    @abstractmethod
    def read_y0(self, y0, ti):
        pass

    def request(self, event, key):
        self.Scheduler.append_request_from_source(event, key)

    @abstractmethod
    def collect_requests(self):
        pass

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

    def disclose(self, msg, who, **kwargs):
        self.Scheduler.append_disclosure_from_source(msg, who, **kwargs)

    @abstractmethod
    def collect_disclosure(self):
        pass

    @abstractmethod
    def fetch_disclosures(self, ds_ms, time):
        pass

    def add_listener(self, impulse, response):
        self.Listeners.add_impulse_response(impulse, response)

    def trigger_external_impulses(self, disclosure, model, time):
        return self.Listeners.apply_shock(disclosure, model, self, time)

    def get_all_impulse_checkers(self):
        return self.Listeners.AllChecker

    def exit_cycle(self):
        if not self.Scheduler.waiting_for_validation():
            self.Scheduler.cycle_completed()

    @abstractmethod
    def print_schedule(self):
        pass

    @count('Observe')
    def initialise_observations(self, ti):
        self.Observer.initialise_observations(self, ti)

    @count('Observe')
    def update_observations(self, ti):
        self.Observer.observe_routinely(self, ti)

    @count('Observe')
    def capture_mid_term_observations(self, ti):
        self.Observer.update_at_mid_term(self, ti)

    @count('Observe')
    def push_observations(self, ti):
        self.Observer.push_observations(ti)

    def set_observation_interval(self, dt):
        self.Observer.ObservationalInterval = dt

    def get_snapshot(self, key, ti):
        return self.Observer.get_snapshot(self, key, ti)

    def output(self, mid=False):
        if mid:
            return self.Observer.AdjustedObservations
        else:
            return self.Observer.Observations

    def clone(self, **kwargs):
        pass


class LeafModel(AbsModel, metaclass=ABCMeta):
    def __init__(self, name, env=None, obs: Observer=None, y0_class=None):
        AbsModel.__init__(self, name, env, obs, y0_class)

    def collect_requests(self):
        if self.Scheduler.waiting_for_collection():
            self.Scheduler.find_next()
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

    def print_schedule(self):
        self.Scheduler.print()


class BranchModel(AbsModel, metaclass=ABCMeta):
    def __init__(self, name, env=None, obs=None, y0_class=None):
        AbsModel.__init__(self, name, env, obs, y0_class)

    def preset(self, ti):
        for v in self.all_models().values():
            v.preset(ti)

    def reset(self, ti):
        for v in self.all_models().values():
            v.reset(ti)

    @abstractmethod
    def all_models(self) -> dict:
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
            self.Scheduler.find_next()
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
            if m is not self:
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

    def get_all_impulse_checkers(self):
        cs = self.Listeners.AllChecker
        for m in self.all_models().values():
            cs += m.get_all_impulse_checkers()
        return cs

    def exit_cycle(self):
        for v in self.all_models().values():
            v.exit_cycle()
        AbsModel.exit_cycle(self)

    def print_schedule(self):
        self.Scheduler.print()
        for m in self.all_models().values():
            m.print_schedule()

    def initialise_observations(self, ti):
        for m in self.all_models().values():
            m.initialise_observations(ti)
        AbsModel.initialise_observations(self, ti)

    def update_observations(self, ti):
        for m in self.all_models().values():
            m.update_observations(ti)
        AbsModel.update_observations(self, ti)

    def capture_mid_term_observations(self, ti):
        for m in self.all_models().values():
            m.capture_mid_term_observations(ti)
        AbsModel.capture_mid_term_observations(self, ti)

    def push_observations(self, ti):
        for m in self.all_models().values():
            m.push_observations(ti)
        AbsModel.push_observations(self, ti)

    def set_observation_interval(self, dt):
        for m in self.all_models().values():
            m.set_observation_interval(dt)
        AbsModel.set_observation_interval(self, dt)
