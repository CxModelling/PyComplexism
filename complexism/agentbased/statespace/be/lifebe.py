import numpy as np
import numpy.random as rd
from complexism.element import StepTicker, Event
from complexism.agentbased import ActiveBehaviour, PassiveBehaviour
from .trigger import StateEnterTrigger

__author__ = 'TimeWz667'
__all__ = ['Reincarnation', 'Cohort', 'LifeRate', 'LifeS', 'AgentImport']


class Reincarnation(PassiveBehaviour):
    def __init__(self, s_death, s_birth):
        PassiveBehaviour.__init__(self, StateEnterTrigger(s_death))
        self.S_death = s_death
        self.S_birth = s_birth
        self.BirthN = 0

    def initialise(self, ti, model):
        pass

    def reset(self, ti, model):
        pass

    def register(self, ag, ti):
        pass

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        model.kill(ag.Name, ti)
        model.birth(n=1, ti=ti, st=self.S_birth)
        self.BirthN += 1

    def fill(self, obs, model, ti):
        obs[self.Name] = self.BirthN

    def match(self, be_src, ags_src, ags_new, ti):
        self.BirthN = be_src.BirthN

    def __repr__(self):
        opt = self.Name, self.S_death.Name, self.S_birth, self.BirthN
        return 'Reincarnation({}, Death:{}, Birth:{}, NBir:{})'.format(*opt)


class Cohort(PassiveBehaviour):
    def __init__(self, s_death):
        PassiveBehaviour.__init__(self, StateEnterTrigger(s_death))
        self.S_death = s_death
        self.DeathN = 0

    def initialise(self, ti, model):
        pass

    def reset(self, ti, model):
        pass

    def register(self, ag, ti):
        pass

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        model.kill(ag.Name, ti)
        self.DeathN += 1

    def fill(self, obs, model, ti):
        obs[self.Name] = self.DeathN

    @staticmethod
    def decorate(name, model, **kwargs):
        s_death = model.DCore.States[kwargs['s_death']]
        be = Cohort(s_death)
        be.Name = name
        model.add_behaviour(be)

    def match(self, be_src, ags_src, ags_new, ti):
        self.DeathN = be_src.DeathN

    def __repr__(self):
        opt = self.Name, self.S_death.Name, self.DeathN
        return 'Cohort({}, Death:{}, NDeath:{})'.format(*opt)


class LifeRate(ActiveBehaviour):
    def __init__(self, s_death, s_birth, rate, dt=1):
        ActiveBehaviour.__init__(self, StepTicker(dt), StateEnterTrigger(s_death))
        self.S_death = s_death.Name
        self.S_birth = s_birth
        self.BirthRate = rate
        self.Dt = dt
        self.BirthN = 0

    def compose_event(self, ti):
        return Event(self.Name, ti)

    def do_action(self, model, todo, ti):
        n = len(model)

        if n <= 0:
            return
        prob = 1 - np.exp(-self.BirthRate * self.Dt)
        n = rd.binomial(n, prob)

        self.BirthN += n
        model.birth(n=n, ti=ti, st=self.S_birth)

    def register(self, ag, ti):
        pass

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        model.kill(ag.Name, ti)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.BirthN

    def __repr__(self):
        return 'BDbyRate({}, BirthRate={})'.format(self.Name, self.BirthRate)

    def match(self, be_src, ags_src, ags_new, ti):
        self.BirthN = be_src.BirthN


class LifeS(ActiveBehaviour):
    def __init__(self, s_death, s_birth, cap, rate, dt=1):
        ActiveBehaviour.__init__(self, StepTicker(dt), StateEnterTrigger(s_death))
        self.S_death = s_death.Name
        self.S_birth = s_birth
        self.Cap = cap
        self.Rate = rate
        self.Dt = dt
        self.BirthN = 0

    def compose_event(self, ti):
        return Event(self.Name, ti)

    def do_action(self, model, todo, ti):
        n = len(model)

        if n <= 0:
            return

        rate = self.Rate * (1 - n / self.Cap)
        prob = 1 - np.exp(-rate * self.Dt)
        if prob > 0:
            n = rd.binomial(n, prob)

            self.BirthN += n
            model.birth(n=n, ti=ti, st=self.S_birth)

    def register(self, ag, ti):
        pass

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        model.kill(ag.Name, ti)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.BirthN

    def __repr__(self):
        return 'S-shape({}, K={}, R={})'.format(self.Name, self.Cap, self.Rate)

    def match(self, be_src, ags_src, ags_new, ti):
        self.BirthN = be_src.BirthN


class AgentImport(PassiveBehaviour):
    def __init__(self, s_birth):
        PassiveBehaviour.__init__(self)
        self.S_birth = s_birth
        self.BirthN = 0

    def initialise(self, ti, model):
        self.BirthN = 0

    def reset(self, ti, model):
        self.BirthN = 0

    def register(self, ag, ti):
        pass

    def fill(self, obs, model, ti):
        obs[self.Name] = self.BirthN

    def shock(self, ti, model, action, **values):
        value = np.floor(values['n'])
        atr = {k: v for k, v in values.items() if k != 'n'}
        if value > 0:
            model.birth(n=value, ti=ti, st=self.S_birth.Name, **atr)
            self.BirthN += value

    def match(self, be_src, ags_src, ags_new, ti):
        self.BirthN = be_src.BirthN

    def __repr__(self):
        opt = self.Name, self.S_birth, self.BirthN
        return 'AgentImport({}, Birth:{}, NBir:{})'.format(*opt)
