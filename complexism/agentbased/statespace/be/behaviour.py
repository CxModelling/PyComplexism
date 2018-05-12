from abc import ABCMeta
from ..modifier import AbsModifier
from complexism.element import AbsTicker
from complexism.agentbased.be import Trigger, TimeIndBehaviour, TimeDepBehaviour

__author__ = 'TimeWz667'
__all__ = ['TimeDepModBehaviour', 'TimeIndModBehaviour']


class TimeDepModBehaviour(TimeDepBehaviour, metaclass=ABCMeta):
    def __init__(self, name, clock: AbsTicker, mod: AbsModifier, trigger=Trigger.NullTrigger):
        TimeDepBehaviour.__init__(self, name, clock, trigger)
        self.ProtoModifier = mod

    def register(self, ag, ti):
        ag.add_modifier(self.ProtoModifier.clone())


class TimeIndModBehaviour(TimeIndBehaviour, metaclass=ABCMeta):
    def __init__(self, name, mod: AbsModifier, trigger=Trigger.NullTrigger):
        TimeIndBehaviour.__init__(self, name, trigger)
        self.ProtoModifier = mod

    def register(self, ag, ti):
        ag.add_modifier(self.ProtoModifier.clone())
