from abc import ABCMeta, abstractmethod, abstractstaticmethod
from .trigger import *
from complexism.mcore import ModelAtom
from complexism.element import AbsTicker, Event

__author__ = 'TimeWz667'
__all__ = ['AbsBehaviour', 'TimeDepBehaviour', 'TimeIndBehaviour']


class AbsBehaviour(metaclass=ABCMeta):
    def __init__(self, trigger=Trigger.NullTrigger):
        self.Trigger = trigger

    @abstractmethod
    def initialise(self, model, ti):
        pass

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

    def impulse_change(self, model, ag, ti):
        pass

    def check_enter(self, ag):
        return self.Trigger.check_enter(ag)

    def impulse_enter(self, model, ag, ti):
        pass

    def check_exit(self, ag):
        return self.Trigger.check_exit(ag)

    def impulse_exit(self, model, ag, ti):
        pass

    def check_foreign(self, model, loc=None):
        return self.Trigger.check_foreign(model, loc)

    def impulse_foreign(self, model, fore, message, ti, **k):
        pass

    def fill(self, obs: dict, model, ti):
        pass

    @staticmethod
    @abstractstaticmethod
    def decorate(name, model, **kwargs):
        pass

    @abstractmethod
    def match(self, be_src, ags_src, ags_new, ti):
        pass


class TimeDepBehaviour(AbsBehaviour, ModelAtom, metaclass=ABCMeta):
    def __init__(self, name, clock: AbsTicker, trigger=Trigger.NullTrigger):
        ModelAtom.__init__(self, name)
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

    def initialise(self, ti, *args, **kwargs):
        self.Clock.initialise(ti)

    def reset(self, ti, *args, **kwargs):
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
    def do_action(self, model, todo, ti):
        """
        Let an event occur
        :param model: source model
        :param todo: action to be done
        :param ti: time
        :type: double
        :return:
        """
        pass


class TimeIndBehaviour(AbsBehaviour, metaclass=ABCMeta):
    def __init__(self, name, trigger=Trigger.NullTrigger):
        AbsBehaviour.__init__(self, trigger)
        self.Name = name

    @property
    def Next(self):
        return Event.NullEvent

    @property
    def TTE(self):
        return float('inf')
