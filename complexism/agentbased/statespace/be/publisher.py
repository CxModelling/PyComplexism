from ...be.behaviour import PassiveBehaviour
from .trigger import StateTrigger
__author__ = 'TimeWz667'
__all__ = ['StateTrack']


class StateTrack(PassiveBehaviour):
    def __init__(self, name, s_src):
        tri = StateTrigger(s_src)
        PassiveBehaviour.__init__(self, name, tri)
        self.S_src = s_src
        self.Value = 0

    def initialise(self, ti, model, *args, **kwargs):
        self.Value = model.Population.count(st=self.S_src)

    def reset(self, ti, *args, **kwargs):
        pass

    def impulse_change(self, model, ag, ti):
        if self.S_src in ag:
            self.Value += 1
        else:
            self.Value -= 1

    def impulse_enter(self, model, ag, ti):
        self.Value += 1

    def impulse_exit(self, model, ag, ti):
        self.Value -= 1

    def match(self, be_src, ags_src, ags_new, ti):
        self.Value = be_src.Value

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value

    def register(self, ag, ti):
        pass

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        model.add_behavior(StateTrack(name, s_src))
