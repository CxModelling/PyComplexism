from abc import ABCMeta, abstractmethod, abstractstaticmethod
from dzdy.abmodel.trigger import *
from dzdy.dcore import Event
from dzdy.mcore import AbsTicker

__author__ = 'TimeWz667'


class AbsBehaviour:
    def __init__(self, name, trigger=Trigger.NullTrigger):
        self.Name = name
        self.Trigger = trigger

    @abstractmethod
    def initialise(self, model, ti):
        pass

    @abstractmethod
    def register(self, ag, ti):
        pass

    def check_tr(self, ag, tr):
        return self.Trigger.check_tr(ag, tr)

    def impulse_tr(self, model, ag, ti):
        pass

    def check_in(self, ag):
        return self.Trigger.check_in(ag)

    def impulse_in(self, model, ag, ti):
        pass

    def check_out(self, ag):
        return self.Trigger.check_out(ag)

    def impulse_out(self, model, ag, ti):
        pass

    def check_foreign(self, model):
        return self.Trigger.check_foreign(model)

    def impulse_foreign(self, model, fore, ti):
        pass

    def fill(self, obs: dict, model, ti):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @staticmethod
    @abstractstaticmethod
    def decorate(name, model, *args, **kwargs):
        pass

    @abstractmethod
    def match(self, be_src, ags_src, ags_new, ti):
        pass


class TimeDepBe:
    def __init__(self, clock: AbsTicker):
        self.Clock = clock
        self.Nxt = Event.NullEvent

    def initialise(self, model, ti):
        self.Clock.initialise(ti)

    @property
    def next(self):
        if self.Nxt is Event.NullEvent:
            self.find_next()
        return self.Nxt

    @property
    def tte(self):
        return self.Nxt.Time

    def find_next(self):
        ti = self.Clock.Next
        self.Nxt = self.compose_event(ti)

    def assign(self, evt):
        self.Nxt = evt

    def exec(self, model, evt):
        self.Clock.update(evt.Time)
        self.do_request(model, evt, evt.Time)
        self.drop_next()

    def drop_next(self):
        self.Nxt = Event.NullEvent

    @abstractmethod
    def compose_event(self, ti):
        pass

    @abstractmethod
    def do_request(self, model, evt, ti):
        pass


class TimeIndBe:
    def __init__(self):
        self.Nxt = Event.NullEvent

    def initialise(self, model, ti):
        pass

    @property
    def next(self):
        return self.Nxt

    @property
    def tte(self):
        return self.Nxt.Time

    def find_next(self):
        pass

    def assign(self, evt):
        pass

    def exec(self, model, evt):
        pass

    def drop_next(self):
        pass


class TimeModBe(TimeDepBe, AbsBehaviour, metaclass=ABCMeta):
    def __init__(self, name, clock, mod, tri=Trigger.NullTrigger):
        TimeDepBe.__init__(self, clock)
        AbsBehaviour.__init__(self, name, tri)
        self.ModPrototype = mod

    def register(self, ag, ti):
        ag.add_mod(self.ModPrototype.clone())


class TimeBe(TimeDepBe, AbsBehaviour, metaclass=ABCMeta):
    def __init__(self, name, clock: AbsTicker, tri=Trigger.NullTrigger):
        TimeDepBe.__init__(self, clock)
        AbsBehaviour.__init__(self, name, tri)

    def match(self, be_src, ags_src, ags_new, ti):
        pass


class ModBe(TimeIndBe, AbsBehaviour, metaclass=ABCMeta):
    def __init__(self, name, mod, tri=Trigger.NullTrigger):
        TimeIndBe.__init__(self)
        AbsBehaviour.__init__(self, name, tri)
        self.ModPrototype = mod

    def register(self, ag, ti):
        ag.add_mod(self.ModPrototype.clone())


class RealTimeBehaviour(TimeIndBe, AbsBehaviour, metaclass=ABCMeta):
    def __init__(self, name, tri):
        TimeIndBe.__init__(self)
        AbsBehaviour.__init__(self, name, tri)
