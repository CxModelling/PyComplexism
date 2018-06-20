from abc import ABCMeta
from ..modifier import AbsModifier
from complexism.element import AbsTicker
from complexism.agentbased.be import Trigger, ActiveBehaviour, PassiveBehaviour

__author__ = 'TimeWz667'
__all__ = ['ActiveModBehaviour', 'PassiveModBehaviour']


class ActiveModBehaviour(ActiveBehaviour, metaclass=ABCMeta):
    def __init__(self, name, clock: AbsTicker, mod: AbsModifier, trigger=Trigger.NullTrigger):
        ActiveBehaviour.__init__(self, name, clock, trigger)
        self.ProtoModifier = mod

    def register(self, ag, ti):
        ag.add_modifier(self.ProtoModifier.clone())


class PassiveModBehaviour(PassiveBehaviour, metaclass=ABCMeta):
    def __init__(self, name, mod: AbsModifier, trigger=Trigger.NullTrigger):
        PassiveBehaviour.__init__(self, name, trigger)
        self.ProtoModifier = mod

    def register(self, ag, ti):
        ag.add_modifier(self.ProtoModifier.clone())
