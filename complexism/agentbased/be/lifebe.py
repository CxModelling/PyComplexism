import numpy as np
import numpy.random as rd
from complexism.element import Clock, Event
from complexism.agentbased import ActiveBehaviour, PassiveBehaviour
from .trigger import AttributeEnterTrigger

__author__ = 'TimeWz667'
__all__ = ['Reincarnation', 'Cohort', 'LifeRate', 'LifeS', 'AgentImport']


class Reincarnation(PassiveBehaviour):
    def __init__(self, name, a_death, a_birth):
        PassiveBehaviour.__init__(self, name, AttributeEnterTrigger(a_death))
        self.Atr_death = a_death
        self.Atr_birth = a_birth
        self.BirthN = 0

    def initialise(self, ti, model):
        pass

    def reset(self, ti, model):
        pass

    def register(self, ag, ti):
        pass

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        model.kill(ag.Name, ti)
        model.birth(n=1, ti=ti, **self.Atr_birth)
        self.BirthN += 1

    def fill(self, obs, model, ti):
        obs[self.Name] = self.BirthN

    @staticmethod
    def decorate(name, model, **kwargs):
        model.add_behaviour(Reincarnation(name, **kwargs))

    def match(self, be_src, ags_src, ags_new, ti):
        self.BirthN = be_src.BirthN

    def __repr__(self):
        opt = self.Name, self.Atr_death, self.Atr_birth, self.BirthN
        return 'Reincarnation({}, Death:{}, Birth:{}, NBir:{})'.format(*opt)


class Cohort(PassiveBehaviour):
    def __init__(self, name, a_death):
        PassiveBehaviour.__init__(self, name, AttributeEnterTrigger(a_death))
        self.Atr_death = a_death
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
        model.Behaviours[name] = Cohort(name, **kwargs)

    def match(self, be_src, ags_src, ags_new, ti):
        self.DeathN = be_src.DeathN

    def __repr__(self):
        opt = self.Name, self.Atr_death, self.DeathN
        return 'Cohort({}, Death:{}, NDeath:{})'.format(*opt)


class LifeRate(ActiveBehaviour):
    def __init__(self, name, a_birth, a_death, rate, dt=1):
        ActiveBehaviour.__init__(self, name, Clock(dt), AttributeEnterTrigger(a_death))
        self.Atr_death = a_death
        self.Atr_birth = a_birth
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
        model.birth(n=n, ti=ti, **self.Atr_birth)

    def register(self, ag, ti):
        pass

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        model.kill(ag.Name, ti)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.BirthN

    @staticmethod
    def decorate(name, model, *args, **kwargs):
        model.add_behaviour(LifeRate(name, **kwargs))

    def __repr__(self):
        return 'BDbyRate({}, BirthRate={})'.format(self.Name, self.BirthRate)

    def match(self, be_src, ags_src, ags_new, ti):
        self.BirthN = be_src.BirthN

    def clone(self, *args, **kwargs):
        pass


class LifeS(ActiveBehaviour):
    def __init__(self, name, a_birth, a_death, cap, rate, dt=1):
        ActiveBehaviour.__init__(self, name, Clock(dt), AttributeEnterTrigger(a_death))
        self.Atr_death = a_death
        self.Atr_birth = a_birth
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

        n = rd.binomial(n, prob)

        self.BirthN += n
        model.birth(n=n, ti=ti, **self.Atr_birth)

    def register(self, ag, ti):
        pass

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        model.kill(ag.Name, ti)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.BirthN

    @staticmethod
    def decorate(name, model, *args, **kwargs):
        model.add_behaviour(LifeS(name, **kwargs))

    def __repr__(self):
        return 'S-shape({}, K={}, R={})'.format(self.Name, self.Cap, self.Rate)

    def match(self, be_src, ags_src, ags_new, ti):
        self.BirthN = be_src.BirthN

    def clone(self, *args, **kwargs):
        pass


class AgentImport(PassiveBehaviour):
    def __init__(self, name, a_birth):
        PassiveBehaviour.__init__(self, name)
        self.Atr_birth = a_birth
        self.BirthN = 0

    def initialise(self, ti, model):
        pass

    def reset(self, ti, model):
        pass

    def register(self, ag, ti):
        pass

    def fill(self, obs, model, ti):
        obs[self.Name] = self.BirthN

    def shock(self, ti, model, action, **values):
        value = np.floor(values['n'])
        if value > 0:
            model.birth(n=value, ti=ti, **self.Atr_birth)
            self.BirthN += value

    @staticmethod
    def decorate(name, model, **kwargs):
        model.add_behaviour(AgentImport(name, **kwargs))

    def match(self, be_src, ags_src, ags_new, ti):
        self.BirthN = be_src.BirthN

    def __repr__(self):
        opt = self.Name, self.Atr_birth, self.BirthN
        return 'AgentImport({}, Birth:{}, NBir:{})'.format(*opt)
