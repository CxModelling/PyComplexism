from abc import ABCMeta, abstractmethod
from complexism.element import Event, RequestSet
from complexism.mcore import Observer, ModelSelector
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

    def fetch_event(self, evt):
        """
        Assign an event to the particle
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

    @abstractmethod
    def initialise(self, ti, *args, **kwargs):
        pass

    @abstractmethod
    def reset(self, ti, *args, **kwargs):
        pass

    def shock(self, ti, source, target, value):
        pass

    def is_compatible(self, **kwargs):
        for k, v in kwargs.items():
            if self.Attributes[k] != v:
                return False
        return True

    def to_json(self):
        js = dict()
        js['Name'] = self.Name
        js['Attributes'] = dict(self.Attributes)
        return js

    def to_snapshot(self):
        return self.to_json()

    def to_data(self):
        dat = dict()
        dat['Name'] = self.Name
        dat.update(self.Attributes)
        return dat

    @abstractmethod
    def clone(self, *args, **kwargs):
        pass


class AbsModel(metaclass=ABCMeta):
    def __init__(self, name, pc=None, obs: Observer=None):
        self.Name = name
        self.Obs = obs
        self.PCore = pc
        self.Requests = RequestSet()
        self.TimeEnd = None

    def initialise(self, ti=None, y0=None):
        if y0:
            self.read_y0(y0, ti)
        self.preset(ti)
        self.drop_next()

    def preset(self, ti):
        self.reset(ti)

    @abstractmethod
    def reset(self, ti):
        pass

    def __getitem__(self, item):
        return self.Obs[item]

    def output(self, mid=False):
        if mid:
            return self.Obs.AdjustedObservations
        else:
            return self.Obs.Observations

    def read_y0(self, y0, ti):
        pass

    def get_snapshot(self, key, ti):
        return self.Obs.get_snapshot(self, key, ti)

    def listen(self, fore, messages, par_src, par_tar, **kwargs):
        pass

    def impulse_foreign(self, fore, message, ti):
        pass

    @property
    def Next(self):
        if self.Requests.is_empty():
            self.find_next()
        return self.Requests.Requests

    @property
    def TTE(self):
        return self.Requests.Time

    def drop_next(self):
        self.Requests.clear()

    @abstractmethod
    def find_next(self):
        pass

    @abstractmethod
    def fetch_requests(self, rs):
        pass

    @abstractmethod
    def execute_requests(self):
        pass

    @abstractmethod
    def do_request(self, req):
        pass

    @count('Observe')
    def initialise_observations(self, ti):
        self.Obs.initialise_observations(self, ti)

    @count('Observe')
    def update_observations(self, ti):
        self.Obs.observe_routinely(self, ti)

    @count('Observe')
    def captureMidTermObservations(self, ti):
        self.Obs.update_at_mid_term(self, ti)

    @count('Observe')
    def push_observations(self, ti):
        self.Obs.push_observations(ti)

    @abstractmethod
    def clone(self, **kwargs):
        pass


class LeafModel(AbsModel, metaclass=ABCMeta):
    def __init__(self, name, pc=None, obs: Observer=None):
        AbsModel.__init__(self, name, pc, obs)

    def fetch_requests(self, rs):
        self.Requests.clear()
        self.Requests.append_requests(rs)

    def execute_requests(self):
        for req in self.Requests:
            self.do_request(req)
        self.drop_next()


class BranchModel(AbsModel, metaclass=ABCMeta):
    def __init__(self, name, pc=None, obs=None):
        AbsModel.__init__(self, name, pc, obs)

    def preset(self, ti):
        for v in self.all_models().values():
            v.preset(ti)
        self.reset_impulse(ti)

    def reset(self, ti):
        for v in self.all_models().values():
            v.reset(ti)
        self.reset_impulse(ti)

    @abstractmethod
    def reset_impulse(self, ti):
        pass

    def select(self, mod):
        return self.get_model(mod)

    def select_all(self, sel):
        return ModelSelector(self.all_models()).select_all(sel)

    def fetch_requests(self, res):
        self.Requests.clear()
        self.Requests.append_requests(res)
        self.pass_down()

    def pass_down(self):
        res = self.Requests.pop_lower_requests()

        for k, v in res.items():
            self.select(k).fetch_requests(v)

    def execute_requests(self):
        for req in self.Requests:
            self.do_request(req)

        ti = self.TTE
        for v in self.all_models().values():
            if v.TTE == ti:
                v.execute_requests()
        self.drop_next()

    @abstractmethod
    def do_request(self, req):
        pass

    @abstractmethod
    def all_models(self)->dict:
        pass

    @abstractmethod
    def get_model(self, k):
        pass

    def initialise_observations(self, ti):
        for m in self.all_models().values():
            m.initialise_observations(ti)
        AbsModel.initialise_observations(self, ti)

    def update_observations(self, ti):
        for m in self.all_models().values():
            m.update_observations(ti)
        AbsModel.update_observations(self, ti)

    def captureMidTermObservations(self, ti):
        for m in self.all_models().values():
            m.captureMidTermObservations(ti)
        AbsModel.captureMidTermObservations(self, ti)

    def push_observations(self, ti):
        for m in self.all_models().values():
            m.push_observations(ti)
        AbsModel.push_observations(self, ti)
