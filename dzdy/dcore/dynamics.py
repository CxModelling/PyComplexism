from abc import abstractmethod, abstractstaticmethod, ABCMeta


class Event:
    NullEvent = None

    def __init__(self, tr, ti):
        """
        Transition with specific event time
        :param tr:
        :param ti:
        """
        self.Time = ti
        self.Transition = tr

    def __gt__(self, ot):
        return self.Time > ot.Time

    def __le__(self, ot):
        return self.Time <= ot.Time

    def __repr__(self):
        return 'Event(Transition: {}, Time: {})'.format(self.Transition, self.Time)

    def __str__(self):
        return '{}: {}'.format(self.Transition, self.Time)


Event.NullEvent = Event(None, float('inf'))


class Transition:
    def __init__(self, name, st, dist):
        """
        Transition
        :param name: Name
        :param st: State after transition happening
        :param dist: probability object with function rvs -> random time
        """
        self.Name = name
        self.Dist = dist
        self.State = st

    def rand(self):
        """
        Randomly sample a time to event
        :return: float: time to event
        """
        return self.Dist.sample()

    def __repr__(self):
        return 'Tr(Name: {}, To: {}, By: {})'.format(self.Name, self.State, str(self.Dist))

    def __str__(self):
        return 'Tr(Name: {}, To: {}, By: {})'.format(self.Name, self.State, str(self.Dist))


class State:
    def __init__(self, name, mod=None):
        self.Name = name
        self.Model = mod

    def next_transition(self, to):
        """
        :param to: target transition
        :return: tuple(transition, time), time = inf if 'to' impossible to be reached
        """
        return self.Model.get_transition(self, to)

    def next_transitions(self):
        """
        :return: list(transition)
        """
        return self.Model.get_transitions(self)

    def next_events(self, ti=0):
        trs = self.next_transitions()
        return [Event(tr, tr.rand()+ti) for tr in trs]

    def next_event(self, ti=0):
        es = self.next_events(ti)
        if es:
            return min(es)
        else:
            return Event.NullEvent

    def exec(self, tr):
        """
        Find the state after transition
        :param tr: event waited for execution
        :return: next state
        """
        return self.Model.exec(self, tr)

    def isa(self, sub):
        """
        Check whether the sub is the sub-state or not
        :param sub: state,
        :return: bool, true if sub is a part of self
        """
        return self.Model.isa(self, sub)

    def __contains__(self, sub):
        return self.Model.isa(self, sub)

    def __repr__(self):
        return str(self.Name)

    def __str__(self):
        return str(self.Name)


class AbsDynamicModel(metaclass=ABCMeta):
    """
    Abstract class of dynamic model. This class and its offspring would never expose to agent
    """
    def __init__(self, name, js):
        self.__Name = name
        self.__JSON = js

    @property
    def Name(self):
        return self.__Name

    @abstractmethod
    def __getitem__(self, item):
        pass

    @abstractmethod
    def get_reachable(self, sts):
        pass

    @abstractmethod
    def get_transition_space(self):
        pass

    @abstractmethod
    def get_state_space(self):
        pass

    @abstractmethod
    def get_transition(self, fr, to):
        pass

    @abstractmethod
    def get_transitions(self, fr):
        pass

    @abstractmethod
    def exec(self, st, tr):
        """
        Execute event based on state
        :param st: state
        :param tr: transition
        :return: next state
        """
        pass

    @abstractmethod
    def isa(self, s0, s1):
        pass

    def to_json(self):
        return self.__JSON

    def __repr__(self):
        return str(self.to_json())


class AbsBlueprint(metaclass=ABCMeta):
    def __init__(self, name):
        self.__Name = name

    @property
    def Name(self):
        return self.__Name

    @abstractmethod
    def generate_model(self, pc, name):
        """
        use a parameter core to generate a dynamic model
        :param name: name of dynamic core
        :param pc: parameter core with all transition pdf
        :return: a dynamic core
        """
        pass

    @abstractmethod
    def to_json(self):
        pass

    def __repr__(self):
        return str(self.to_json())
