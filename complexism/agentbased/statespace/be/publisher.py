from ...be.behaviour import PassiveBehaviour
from .trigger import StateTrigger, DoubleStateTrigger
__author__ = 'TimeWz667'
__all__ = ['StateTrack']


class StateTrack(PassiveBehaviour):
    def __init__(self, s_src):
        tri = StateTrigger(s_src)
        PassiveBehaviour.__init__(self, tri)
        self.S_src = s_src
        self.Value = 0

    def initialise(self, ti, model):
        self.Value = self.__evaluate(model)
        model.disclose('update value to {}'.format(self.Value), self.Name, v1=self.Value)

    def reset(self, ti, model):
        pass

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        if self.S_src in ag:
            self.__change_value(model, 1)
        else:
            self.__change_value(model, -1)

    def impulse_enter(self, model, ag, ti, args=None):
        self.__change_value(model, 1)

    def impulse_exit(self, model, ag, ti, args=None):
        self.__change_value(model, -1)

    def __evaluate(self, model):
        return model.Population.count(st=self.S_src)

    def __change_value(self, model, dv):
        v0, v1 = self.Value, self.Value + dv
        self.Value = v1
        model.disclose('update value to {}'.format(v1), self.Name, v0=v0, v1=v1)

    def match(self, be_src, ags_src, ags_new, ti):
        self.Value = be_src.Value

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value

    def register(self, ag, ti):
        pass


class StateRatioTrack(PassiveBehaviour):
    def __init__(self, s_num, s_den):
        tri = DoubleStateTrigger(s_num, s_den)
        PassiveBehaviour.__init__(self, tri)
        self.S_num = s_num
        self.S_den = s_den
        self.ValueNum = 0
        self.ValueDen = 0

    def initialise(self, ti, model):
        self.ValueNum = model.Population.count(st=self.S_num)
        self.ValueDen = model.Population.count(st=self.S_den)

    def reset(self, ti, model):
        self.ValueNum = model.Population.count(st=self.S_num)
        self.ValueDen = model.Population.count(st=self.S_den)

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        a0, b0 = args_pre
        a1, b1 = args_post
        if a0 and not a1:
            self.ValueNum -= 1
        elif a1 and not a0:
            self.ValueNum += 1

        if b0 and not b1:
            self.ValueDen -= 1
        elif b1 and not b0:
            self.ValueDen += 1
        model.disclose('update value', self.Name, v=self.ValueNum/self.ValueDen)

    def impulse_enter(self, model, ag, ti, args=None):
        a, b = args
        if a:
            self.ValueNum += 1
        if b:
            self.ValueDen += 1
        model.disclose('update value', self.Name, v=self.ValueNum/self.ValueDen)

    def impulse_exit(self, model, ag, ti, args=None):
        a, b = args
        if a:
            self.ValueNum -= 1
        if b:
            self.ValueDen -= 1
        model.disclose('update value', self.Name, v=self.ValueNum/self.ValueDen)

    def match(self, be_src, ags_src, ags_new, ti):
        self.ValueNum = be_src.ValueNum
        self.ValueDen = be_src.ValueDen

    def fill(self, obs, model, ti):
        obs[self.Name] = self.ValueNum / self.ValueDen

    def register(self, ag, ti):
        pass
