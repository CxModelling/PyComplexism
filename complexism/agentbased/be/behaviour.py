from abc import ABCMeta, abstractmethod
from .trigger import *
from mcore import ModelAtom
from element import AbsTicker, Event

__author__ = 'TimeWz667'
__all__ = ['AbsBehaviour', 'PassiveBehaviour', 'ActiveBehaviour']


class AbsBehaviour(ModelAtom, metaclass=ABCMeta):
    def __init__(self, trigger=Trigger.NullTrigger):
        ModelAtom.__init__(self, type(self))
        self.Trigger = trigger

    @abstractmethod
    def register(self, ag, ti):
        pass

    def check_event(self, ag, evt):
        return self.Trigger.check_event(ag, evt)

    def check_pre_change(self, ag):
        return self.Trigger.check_pre_change(ag)

    def check_post_change(self, ag):
        return self.Trigger.check_post_change(ag)

    def check_change(self, pre, post):
        return self.Trigger.check_change(pre, post)

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        pass

    def check_enter(self, ag):
        return self.Trigger.check_enter(ag)

    def impulse_enter(self, model, ag, ti, args=None):
        pass

    def check_exit(self, ag):
        return self.Trigger.check_exit(ag)

    def impulse_exit(self, model, ag, ti, args=None):
        pass

    def fill(self, obs: dict, model, ti):
        pass

    @abstractmethod
    def match(self, be_src, ags_src, ags_new, ti):
        pass


class ActiveBehaviour(AbsBehaviour, metaclass=ABCMeta):
    def __init__(self, clock: AbsTicker, trigger=Trigger.NullTrigger):
        AbsBehaviour.__init__(self, trigger)
        self.Clock = clock

    def find_next(self):
        return self.compose_event(self.Clock.Next)

    def execute_event(self):
        """
        Do not use
        """
        pass

    def operate(self, model):
        event = self.Next
        time = event.Time
        self.Clock.update(time)
        self.do_action(model, event.Todo, time)
        self.drop_next()

    def initialise(self, ti, model):
        self.Clock.initialise(ti)

    def reset(self, ti, model):
        self.Clock.initialise(ti)

    @abstractmethod
    def compose_event(self, ti):
        """
        Compose the next event
        :param ti: current time
        :return:
        :rtype:
        """
        pass

    @abstractmethod
    def do_action(self, model, td, ti):
        """
        Let an event occur
        :param model: source model
        :param td: action to be done
        :param ti: time
        :type: double
        :return:
        """
        pass


class PassiveBehaviour(AbsBehaviour, metaclass=ABCMeta):
    def __init__(self, trigger=Trigger.NullTrigger):
        AbsBehaviour.__init__(self, trigger)

    @property
    def Next(self):
        return Event.NullEvent

    @property
    def TTE(self):
        return float('inf')

    def drop_next(self):
        return

    def find_next(self):
        pass

    def execute_event(self):
        pass
