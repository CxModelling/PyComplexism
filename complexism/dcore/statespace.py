from complexism.element import Event
from .dynamics import AbsDynamicModel, Stock
from abc import ABCMeta, abstractmethod

__author__ = 'TimeWz667'
__all__ = ['Transition', 'State', 'AbsStateSpaceModel']


class Transition:
    def __init__(self, name, st, dist):
        """
        Transition
        :param name: Name
        :type name: str
        :param st: State after transition happening
        :type st: State
        :param dist: probability object with function rvs -> random time
        """
        self.Name = name
        self.Dist = dist
        self.State = st

    def rand(self, attr=None):
        """
        Randomly sample a time to event
        :param attr: parent nodes
        :type attr: dict
        :return: time to event
        :rtype: float
        """
        return self.Dist.sample(attr)

    def __repr__(self):
        return 'Tr(Name: {}, To: {}, By: {})'.format(self.Name, self.State, self.Dist.Field)

    def __str__(self):
        return 'Tr(Name: {}, To: {}, By: {})'.format(self.Name, self.State, self.Dist.Field)


class State(Stock):
    def __init__(self, name, mod=None):
        Stock.__init__(self, name, mod)

    def next_transition(self, to):
        """
        :param to: target transition
        :type to: State
        :return: transition, time; time = inf if 'to' impossible to be reached
        :rtype: tuple
        """
        return self.Model.get_transition(self, to)

    def next_transitions(self):
        """
        :return: a list of transition
        :rtype: list
        """
        return self.Model.get_transitions(self)

    def next_events(self, ti=0, attr=None):
        """
        Find possible events to occur
        :param ti: current time
        :type ti: float, int
        :param attr: external attributes for querying next events
        :type attr: dict
        :return: list of candidate events
        :rtype: list
        """
        trs = self.next_transitions()
        return [Event(tr, tr.rand(attr)+ti, tr.Name) for tr in trs]

    def next_event(self, ti=0, attr=None):
        """
        Find the next event
        :param ti: current time
        :type ti: float, int
        :param attr: external attributes for querying next events
        :type attr: dict
        :return: the nearest events
        :rtype: Event
        """
        es = self.next_events(ti, attr)
        if es:
            return min(es)
        else:
            return Event.NullEvent

    def isa(self, sub):
        """
        Check whether the sub is the sub-state or not
        :param sub: state
        :param sub: State
        :return: true if sub is a part of self
        :rtype: bool
        """
        return self.Model.isa(self, sub)

    def __contains__(self, sub):
        return self.Model.isa(self, sub)


class AbsStateSpaceModel(AbsDynamicModel, metaclass=ABCMeta):
    """
    Abstract class of dynamic model. This class and its offspring would never expose to agent
    """
    def __init__(self, name, js):
        AbsDynamicModel.__init__(self, name, js)

    def compose_stock(self, key):
        return self.get_state_space()[key]

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
    def isa(self, s0, s1):
        pass
