from dzdy.abmodel import RealTimeBehaviour, StateInTrigger, StateTrigger, TimeBe, TimeModBe, DirectModifier, GloRateModifier
from dzdy.mcore import Clock
from dzdy.dcore import Event
from dzdy.util import DemographySimplified
import numpy as np
import pandas as pd
import numpy.random as rd


__author__ = 'TimeWz667'


class Reincarnation(RealTimeBehaviour):
    def __init__(self, name, s_death, s_birth):
        RealTimeBehaviour.__init__(self, name, StateInTrigger(s_death))
        self.S_death = s_death
        self.S_birth = s_birth
        self.N_birth = 0

    def initialise(self, model, ti):
        pass

    def register(self, ag, ti):
        pass

    def impulse_tr(self, model, ag, ti):
        model.kill(ag.Name, ti)
        model.birth(self.S_birth, ti)
        self.N_birth += 1

    def __repr__(self):
        opt = self.Name, self.S_death.Name, self.S_birth, self.N_birth
        return 'Reincarnation({}, Death:{}, Birth:{}, NBir:{})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_death = model.DCore.States[kwargs['s_death']]
        model.Behaviours[name] = Reincarnation(name, s_death, kwargs['s_birth'])

    def fill(self, obs, model, ti):
        obs[self.Name] = self.N_birth

    def match(self, be_src, ags_src, ags_new, ti):
        self.N_birth = be_src.N_birth


class Cohort(RealTimeBehaviour):
    def __init__(self, name, s_death):
        RealTimeBehaviour.__init__(self, name, StateInTrigger(s_death))
        self.S_death = s_death
        self.N_dead = 0

    def initialise(self, model, ti):
        pass

    def register(self, ag, ti):
        pass

    def impulse_tr(self, model, ag, ti):
        model.kill(ag.Name, ti)
        self.N_dead += 1

    def __repr__(self):
        opt = self.Name, self.S_death.Name, self.N_dead
        return 'Cohort({}, Death:{}, NDea:{})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_death = model.DCore.States[kwargs['s_death']]
        model.Behaviours[name] = Cohort(name, s_death)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.N_dead

    def match(self, be_src, ags_src, ags_new, ti):
        self.N_dead = be_src.N_dead


class LifeRate(TimeBe):
    def __init__(self, name, s_birth, s_death, rate, dt=1):
        TimeBe.__init__(self, name, Clock(dt), StateInTrigger(s_death))
        self.S_death = s_death.Name
        self.S_birth = s_birth
        self.BirthRate = rate
        self.Dt = dt
        self.N_birth = 0

    def register(self, ag, ti):
        pass

    def impulse_tr(self, model, ag, ti):
        model.kill(ag.Name, ti)

    def do_request(self, model, evt, ti):
        n = model.Pop.count()

        if n <= 0:
            return
        prob = 1 - np.exp(-self.BirthRate*self.Dt)
        n = rd.binomial(n, prob)

        self.N_birth += n
        for _ in range(n):
            model.birth(self.S_birth, ti)

    def compose_event(self, ti):
        return Event(self.Name, ti)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.N_birth

    @staticmethod
    def decorate(name, model, *args, **kwargs):
        s_death = model.DCore.States[kwargs['s_death']]
        dt = kwargs['dt'] if 'dt' in kwargs else 1
        model.Behaviours[name] = LifeRate(name, kwargs['s_birth'], s_death, kwargs['rate'], dt)

    def __repr__(self):
        return 'BDbyRate({}, BirthRate={})'.format(self.Name, self.BirthRate)

    def match(self, be_src, ags_src, ags_new, ti):
        self.N_birth = be_src.N_birth


class LifeS(TimeBe):
    def __init__(self, name, s_birth, s_death, cap, rate, dt=1):
        TimeBe.__init__(self, name, Clock(dt), StateInTrigger(s_death))
        self.S_death = s_death.Name
        self.S_birth = s_birth
        self.Cap = cap
        self.Rate = rate
        self.Dt = dt
        self.N_birth = 0

    def register(self, ag, ti):
        pass

    def impulse_tr(self, model, ag, ti):
        model.kill(ag.Name, ti)

    def do_request(self, model, evt, ti):
        n = model.Pop.count()

        if n <= 0:
            return
        rate = self.Rate * (1 - n / self.Cap)

        n = rd.binomial(n, 1 - np.exp(-rate*self.Dt))

        self.N_birth += n
        for _ in range(n):
            model.birth(self.S_birth, ti)

    def compose_event(self, ti):
        return Event(self.Name, ti)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.N_birth

    @staticmethod
    def decorate(name, model, *args, **kwargs):
        s_death = model.DCore.States[kwargs['s_death']]
        dt = kwargs['dt'] if 'dt' in kwargs else 1
        model.Behaviours[name] = LifeS(name, kwargs['s_birth'], s_death, kwargs['cap'], kwargs['rate'], dt)

    def __repr__(self):
        return 'S-shape({}, K={}, R={})'.format(self.Name, self.Cap, self.Rate)

    def match(self, be_src, ags_src, ags_new, ti):
        self.N_birth = be_src.N_birth


class LifeLeeCarter(TimeModBe):
    def __init__(self, name, demo, s_birth, s_death, t_death):
        mod = DirectModifier(name, t_death)
        TimeModBe.__init__(self, name, Clock(dt=1), mod, StateTrigger(s_death))
        self.Demography = demo
        self.S_death = s_death.Name
        self.S_birth = s_birth
        self.T_death = t_death.Name
        self.Pop0 = 0
        self.Rec_Death = list()
        # value

    def initialise(self, model, ti):
        self.Clock.initialise(ti)
        for ag in model.agents:
            ag.shock(self.Name, self.Demography.sample_time_to_death(ag.Info, ti)[0], ti)

        self.Pop0 = model.Pop.count()

    def impulse_tr(self, model, ag, ti):
        self.Rec_Death.append(ag.Info)
        model.kill(ag.Name, ti)

    def do_request(self, model, evt, ti):
        to_kill = []
        for ag in model.agents:
            if ag.Info['Age'] >= 99:
                to_kill.append(ag)
            else:
                ag.Info['Age'] += 1

        for ag in to_kill:
            self.Rec_Death.append(ag.Info)
            model.kill(ag.Name, ti)

        nb = rd.poisson(self.Demography.get_n_birth(np.floor(ti), self.Pop0))
        # nb = self.Demography.get_n_birth(np.floor(ti), self.Pop0)
        nb = round(nb)
        ags = model.birth(self.S_birth, ti, n=nb, info={'Age': 0})
        for ag in ags:
            ag.shock(self.Name, self.Demography.sample_time_to_death(ag.Info, ti)[0], ti)

    def compose_event(self, ti):
        return Event(self.Name, ti)

    def __repr__(self):
        opt = self.Name, self.T_death, self.Demography.StartYear
        return 'LeeCarterModel({} on {}, from {})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_death = model.DCore.States[kwargs['s_death']]
        t_death = model.DCore.Transitions[kwargs['t_death']]
        demo = kwargs['demo']
        model.Pop.append_fill(demo.get_fill_age_sex())
        model.Behaviours[name] = LifeLeeCarter(name, demo, kwargs['s_birth'], s_death, t_death)

    def fill(self, obs, model, ti):
        dat = pd.DataFrame.from_records(self.Rec_Death)
        if not self.Rec_Death:
            return
        for k, v in dat.groupby('Sex').mean().iterrows():
            obs['{}.DeaAge{}'.format(self.Name, k[0])] = float(v)

        for k, v in dat.groupby('Sex').count().iterrows():
            obs['{}.DeaNum{}'.format(self.Name, k[0])] = float(v)
        self.Rec_Death.clear()

    def match(self, be_src, ags_src, ags_new, ti):
        for ag in ags_new.values():
            self.register(ag, ti)


class TimeSeriesLife(TimeModBe):
    def __init__(self, name, demo, s_birth, s_death, t_death):
        mod = GloRateModifier(name, t_death)
        TimeModBe.__init__(self, name, Clock(dt=0.5), mod, StateTrigger(s_death))
        self.Demography = demo
        self.S_death = s_death.Name
        self.S_birth = s_birth.Name
        self.T_death = t_death.Name
        self.NDeath = 0
        self.NBirth = 0
        self.LastUpdate = 0

    def initialise(self, model, ti):
        self.Clock.initialise(ti)
        nb = rd.binomial(model.Pop.count(), self.Demography.RateBirth(ti))
        # nb = self.Demography.get_n_birth(np.floor(ti), self.Pop0)
        self.NBirth += nb
        model.birth(self.S_birth, ti, n=nb)
        self.ModPrototype.Val = self.Demography.RateDeath(ti)
        for ag in model.agents:
            ag.modify(self.Name, ti)

    def impulse_tr(self, model, ag, ti):
        self.NDeath += 1
        model.kill(ag.Name, ti)

    def do_request(self, model, evt, ti):
        nb = rd.binomial(model.Pop.count(), self.Demography.RateBirth(ti))
        # nb = self.Demography.get_n_birth(np.floor(ti), self.Pop0)
        self.NBirth += nb
        model.birth(self.S_birth, ti, n=nb)
        self.ModPrototype.Val = self.Demography.RateDeath(ti)
        for ag in model.agents:
            ag.modify(self.Name, ti)

    def compose_event(self, ti):
        return Event(self.Name, ti)

    def __repr__(self):
        opt = self.Name, self.T_death, self.Demography.StartYear
        return 'TimeSeriesLife({} on {}, from {})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_death = model.DCore.States[kwargs['s_death']]
        t_death = model.DCore.Transitions[kwargs['t_death']]

        model.Behaviours[name] = TimeSeriesLife(name, kwargs['demo'], kwargs['s_birth'], s_death, t_death)

    def fill(self, obs, model, ti):
        obs['{}.DeaNum'.format(self.Name)] = self.NDeath
        obs['{}.BirNum'.format(self.Name)] = self.NBirth

    def match(self, be_src, ags_src, ags_new, ti):
        for ag in ags_new.values():
            self.register(ag, ti)
