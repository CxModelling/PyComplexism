__author__ = 'TimeWz667'


__all__ = ['Trigger', 'TransitionTrigger', 'StateTrigger', 'StateInTrigger',
           'StateOutTrigger', 'ForeignTrigger', 'ForeignSetTrigger',
           'NullTrigger']


class Trigger:
    NullTrigger = None

    def check_tr(self, ag, tr):
        return False

    def check_in(self, ag):
        return False

    def check_out(self, ag):
        return False

    def check_foreign(self, model):
        return False

Trigger.NullTrigger = Trigger()


class TransitionTrigger(Trigger):
    def __init__(self, tr):
        self.Tr = tr

    def check_tr(self, ag, tr):
        return self.Tr == tr


class StateTrigger(Trigger):
    def __init__(self, st):
        self.State = st

    def check_tr(self, ag, tr):
        return (self.State in ag.State) ^ (self.State in ag.State.exec(tr))

    def check_in(self, ag):
        return self.State in ag.State

    def check_out(self, ag):
        return self.State in ag.State


class StateOutTrigger(Trigger):
    def __init__(self, st):
        self.State = st

    def check_tr(self, ag, tr):
        return self.State in ag.State and (self.State not in ag.State.exec(tr))

    def check_out(self, ag):
        return self.State in ag.State


class StateInTrigger(Trigger):
    def __init__(self, st):
        self.State = st

    def check_tr(self, ag, tr):
        return (self.State not in ag.State) and (self.State in ag.State.exec(tr))

    def check_in(self, ag):
        return self.State in ag.State


class ForeignTrigger(Trigger):
    def __init__(self, model, nod):
        self.Model = model
        self.Node = nod

    def check_foreign(self, model):
        return self.Model is model.Name


class ForeignSetTrigger(Trigger):
    def __init__(self, nod):
        self.Models = list()
        self.Node = nod

    def append(self, mod):
        self.Models.append(mod)

    def check_foreign(self, model):
        return model.Name in self.Models
