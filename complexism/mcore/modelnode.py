from complexism.element import Event, RequestSet
from complexism.mcore import Observer, ModelSelector
from abc import ABCMeta, abstractmethod

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
    def __init__(self, name, obs: Observer):
        self.Name = name
        self.Obs = obs
        self.Requests = RequestSet()
        self.TimeEnd = None

    def initialise(self, ti=None, y0=None):
        if y0:
            self.read_y0(y0, ti)
        self.preset(ti)
        self.drop_next()

    def preset(self, ti):
        pass

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

    def listen(self, model_src, par_src, par_tar, **kwargs):
        pass

    def listen_multi(self, model_src_all, par_src, par_tar, **kwargs):
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

    def initialise_observations(self, ti):
        self.Obs.initialise_observations(self, ti)

    def update_observations(self, ti):
        self.Obs.observe_routinely(self, ti)

    def captureMidTermObservations(self, ti):
        self.Obs.update_at_mid_term(self, ti)

    def push_observations(self, ti):
        self.Obs.push_observations(ti)

    @abstractmethod
    def clone(self, **kwargs):
        pass


class LeafModel(AbsModel, metaclass=ABCMeta):
    def __init__(self, name, obs):
        AbsModel.__init__(self, name, obs)

    def fetch_requests(self, rs):
        self.Requests.clear()
        self.Requests.append_requests(rs)

    def execute_requests(self):
        for req in self.Requests:
            self.do_request(req)
        self.drop_next()


class BranchModel(AbsModel, metaclass=ABCMeta):
    def __init__(self, name, obs):
        AbsModel.__init__(self, name, obs)
        self.Models = dict()

    def select(self, mod):
        return self.Models[mod]

    def select_all(self, sel):
        return ModelSelector(self.Models).select_all(sel)

    def fetch_requests(self, res):
        self.Requests.clear()
        self.Requests.append_requests(res)
        self.pass_down()

    def pass_down(self):
        res = self.Requests.pop_lower_requests()
        nest = dict()
        for req in res:
            m, req = req.down()
            try:
                nest[m].append(req)
            except KeyError:
                nest[m] = [req]

        for k, v in nest.items():
            self.select(k).fetch(v)

    def execute_requests(self):
        for req in self.Requests:
            self.do_request(req)

        for v in self.Models.values():
            if v.TTE == self.TTE:
                v.execute_requests()
        self.drop_next()

    @abstractmethod
    def do_request(self, req):
        pass
