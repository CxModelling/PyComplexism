import numpy as np
import numpy.random as rd
from element import StepTicker, ScheduleTicker, Event
from complexism.agentbased import ActiveBehaviour, PassiveBehaviour
from .trigger import StateEnterTrigger
from ..modifier import LocRateModifier
from .behaviour import ActiveModBehaviour

__author__ = 'TimeWz667'
__all__ = ['Reincarnation', 'Cohort', 'LifeRate', 'LifeS', 'AgentImport',
           'BirthAgeingDeathLeeCarter', 'CohortLeeCarter']


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
        model.kill(ag.Name, ti, self.Name)
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

            model.birth(n=n, ti=ti, st=self.S_birth)

    def register(self, ag, ti):
        pass

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        model.kill(ag.Name, ti)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Rate * (1 - len(model) / self.Cap)

    def __repr__(self):
        return 'S-shape({}, K={}, R={})'.format(self.Name, self.Cap, self.Rate)

    def match(self, be_src, ags_src, ags_new, ti):
        pass


class BirthAgeingDeathLeeCarter(ActiveModBehaviour):
    def __init__(self, s_death, t_die, s_birth, dlc):
        mod = LocRateModifier(t_die)
        years = range(dlc.YearStart, dlc.YearEnd + 1)
        ActiveModBehaviour.__init__(self, ScheduleTicker(years), mod, StateEnterTrigger(s_death))
        self.S_death = s_death.Name
        self.S_birth = s_birth
        self.T_die = t_die
        self.LeeCarter = dlc
        self.DeathRates = self.LeeCarter.get_death_rate(self.LeeCarter.YearStart)
        self.BirPrF = self.LeeCarter.get_prob_female_at_birth(self.LeeCarter.YearStart)
        self.SexAgeSam = self.LeeCarter.get_population_sampler(self.LeeCarter.YearStart)

    def initialise(self, ti, model):
        ti = max(ti, self.LeeCarter.YearStart)
        self.__update_data(ti)
        ActiveModBehaviour.initialise(self, ti, model)
        self.__shock(model, ti)

    def reset(self, ti, model):
        self.Clock.initialise(ti)
        self.__update_data(ti)
        ActiveModBehaviour.reset(self, ti, model)
        self.__shock(model, ti)

    def compose_event(self, ti):
        return Event('Ageing', float(ti))

    def do_action(self, model, td, ti):
        if td == 'Ageing':
            self.__update_data(ti)

            # Ageing
            to_delete = list()
            for ag in model.agents:
                ag['Age'] += 1
                if ag['Age'] >= 100:
                    to_delete.append(ag)

            for ag in to_delete:
                model.kill(ag.Name, ti)
                model.Observer.record(ag, 'Die', ti)

            # Birth
            n = len(model)
            br = self.LeeCarter.get_birth_rate(ti)
            if n <= 0:
                return
            prob = 1 - np.exp(-br['Female'])
            ags = model.birth(n=rd.binomial(n, prob), ti=ti, st=self.S_birth)
            for ag in ags:
                ag['Sex'] = 'Female'
                ag['Age'] = 0

            if n <= 0:
                return
            prob = 1 - np.exp(-br['Male'])
            ags = model.birth(n=rd.binomial(n, prob), ti=ti, st=self.S_birth)
            for ag in ags:
                ag['Sex'] = 'Male'
                ag['Age'] = 0

            # Update death rate
            self.__shock(model, ti)
            model.disclose('Ageing', self.Name)
            model.disclose('Birth', self.Name)

    def register(self, ag, ti):
        ActiveModBehaviour.register(self, ag, ti)
        if 'Sex' not in ag.Attributes:
            ag['Sex'], ag['Age'] = self.SexAgeSam()

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        model.kill(ag.Name, ti)

    def match(self, be_src, ags_src, ags_new, ti):
        pass

    def fill(self, obs, model, ti):
        try:
            obs['SexRatio'] = model.Population.count(Sex='Male') / model.Population.count(Sex='Female')
        except ZeroDivisionError:
            obs['SexRatio'] = float('inf')

        ages = [ag['Age'] for ag in model.agents]

        obs['AvgAge'] = np.mean(ages)

    def __update_data(self, ti):
        self.DeathRates = self.LeeCarter.get_death_rate(ti)
        self.BirPrF = self.LeeCarter.get_prob_female_at_birth(ti)
        self.SexAgeSam = self.LeeCarter.get_population_sampler(ti)

    def __shock(self, model, ti):
        for ag in model.agents:
            dr = self.DeathRates[ag['Sex']][ag['Age']]
            ag.shock(ti, None, self.Name, value=dr)
        model.disclose('Update death rates', self.Name)


class CohortLeeCarter(ActiveModBehaviour):
    def __init__(self, s_death, t_die, dlc):
        mod = LocRateModifier(t_die)
        years = range(dlc.YearStart, dlc.YearEnd + 1)
        ActiveModBehaviour.__init__(self, ScheduleTicker(years), mod, StateEnterTrigger(s_death))
        self.S_death = s_death.Name
        self.T_die = t_die
        self.LeeCarter = dlc
        self.DeathRates = self.LeeCarter.get_death_rate(self.LeeCarter.YearStart)
        self.SexAgeSam = self.LeeCarter.get_population_sampler(self.LeeCarter.YearStart)
        self.MaleAgeSam = self.LeeCarter.get_population_sampler(self.LeeCarter.YearStart, sex='Male')
        self.FemaleAgeSam = self.LeeCarter.get_population_sampler(self.LeeCarter.YearStart, sex='Female')

    def initialise(self, ti, model):
        ti = max(ti, self.LeeCarter.YearStart)
        self.__update_data(ti)
        ActiveModBehaviour.initialise(self, ti, model)
        self.__shock(model, ti)

    def reset(self, ti, model):
        self.Clock.initialise(ti)
        self.__update_data(ti)
        ActiveModBehaviour.reset(self, ti, model)
        self.__shock(model, ti)

    def compose_event(self, ti):
        return Event('Ageing', float(ti))

    def do_action(self, model, td, ti):
        if td == 'Ageing':
            self.__update_data(ti)

            # Ageing
            to_delete = list()
            for ag in model.agents:
                ag['Age'] += 1
                if ag['Age'] >= 100:
                    to_delete.append(ag)

            for ag in to_delete:
                model.kill(ag.Name, ti)
                model.Observer.record(ag, 'Die', ti)

            self.__shock(model, ti)

            model.disclose('Ageing', self.Name)

    def register(self, ag, ti):
        ActiveModBehaviour.register(self, ag, ti)
        if 'Sex' not in ag.Attributes:
            ag['Sex'], ag['Age'] = self.SexAgeSam()
        elif 'Age' not in ag.Attributes:
            if ag['Sex'] == 'Female':
                ag['Age'] = self.FemaleAgeSam()
            else:
                ag['Age'] = self.MaleAgeSam()

            dr = self.DeathRates[ag['Sex']][ag['Age']]
            ag.shock(ti, None, self.Name, value=dr)

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        model.kill(ag.Name, ti)

    def match(self, be_src, ags_src, ags_new, ti):
        pass

    def fill(self, obs, model, ti):
        try:
            obs['SexRatio'] = model.Population.count(Sex='Male') / model.Population.count(Sex='Female')
        except ZeroDivisionError:
            obs['SexRatio'] = float('inf')

        ages = [ag['Age'] for ag in model.agents]

        obs['AvgAge'] = np.mean(ages)

    def __update_data(self, ti):
        self.DeathRates = self.LeeCarter.get_death_rate(ti)
        self.SexAgeSam = self.LeeCarter.get_population_sampler(ti)

    def __shock(self, model, ti):
        for ag in model.agents:
            dr = self.DeathRates[ag['Sex']][ag['Age']]
            ag.shock(ti, None, self.Name, value=dr)
        model.disclose('Update death rates', self.Name)


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
