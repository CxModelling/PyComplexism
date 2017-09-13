from dzdy.abmodel.behaviour import *
from dzdy.abmodel.modifier import *
__author__ = 'TimeWz667'


class ForeignShock(ModBe):
    def __init__(self, name, mod_src, par_src, t_tar):
        tri = ForeignTrigger(mod_src)
        mod = GloRateModifier(name, t_tar)
        ModBe.__init__(self, name, mod, tri)
        self.RefMod, self.RefPar = mod_src, par_src
        self.Target = t_tar.Name
        self.Val = 0

    def set_source(self, mod_src, par_src, par_tar=None):
        self.RefMod, self.RefPar = mod_src, par_src
        self.Trigger.append(mod_src)

    def initialise(self, model, ti):
        self.shock(model, ti)

    def impulse_foreign(self, model, fore, ti):
        self.Val = fore[self.RefPar]
        self.shock(model, ti)

    def shock(self, model, ti):
        self.ModPrototype.Val = self.Val
        for ag in model.agents:
            ag.modify(self.Name, ti)

    def __repr__(self):
        opt = self.Name, '{}@{}'.format(self.RefMod, self.RefPar), self.Target, self.Val
        return 'Foreign({}, {} on {}, Value={})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        target = model.DCore.Transitions[kwargs['t_tar']]
        mod_src = kwargs['mod_src'] if 'mod_src' in kwargs else None
        par_src = kwargs['par_src'] if 'par_src' in kwargs else None
        model.Behaviours[name] = ForeignShock(name, mod_src, par_src, target)

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.Val
        return obs

    def match(self, be_src, ags_src, ags_new, ti):
        self.Val = be_src.Val
        for ag_new, ag_src in zip(ags_new.values(), ags_src.values()):
            self.register(ag_new, ti)
            ag_new.Mods[self.Name].Val = ag_src.Mods[self.Name].Val


class ForeignAddShock(ModBe):
    def __init__(self, name, t_tar):
        tri = ForeignSetTrigger()
        mod = GloRateModifier(name, t_tar)
        ModBe.__init__(self, name, mod, tri)
        self.Ref = dict()
        self.Target = t_tar.Name
        self.Values = dict()
        self.Sum = 0

    def set_source(self, mod_src, par_src, par_tar=None):
        self.Ref[mod_src] = par_src
        self.Values[mod_src] = 0
        self.Trigger.append(mod_src)

    def initialise(self, model, ti):
        self.shock(model, ti)

    def impulse_foreign(self, model, fore, ti):
        self.Values[fore.Name] = fore[self.Ref[fore.Name]]
        self.shock(model, ti)

    def shock(self, model, ti):
        self.ModPrototype.Val = self.Sum =  sum(self.Values.values())
        for ag in model.agents:
            ag.modify(self.Name, ti)

    def __repr__(self):
        opt = self.Name, self.Target, self.Sum
        return 'ForeignSet({} on {}, Value={})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        target = model.DCore.Transitions[kwargs['t_tar']]
        m = ForeignAddShock(name, target)
        model.Behaviours[name] = m
        return m

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.Sum
        return obs

    def match(self, be_src, ags_src, ags_new, ti):
        self.Sum = be_src.Sum
        self.Values.update(be_src.Values)
        for ag_new, ag_src in zip(ags_new.values(), ags_src.values()):
            self.register(ag_new, ti)
            ag_new.Mods[self.Name].Val = ag_src.Mods[self.Name].Val


class BirthListener(RealTimeBehaviour):
    def __init__(self, name, s_birth):
        RealTimeBehaviour.__init__(self, name, ForeignTrigger())
        self.S_birth = s_birth
        self.N_birth = 0

    def initialise(self, model, ti):
        pass

    def register(self, ag, ti):
        pass

    def impulse_tr(self, model, ag, ti):
        model.birth(self.S_birth, ti)
        self.N_birth += 1

    def __repr__(self):
        opt = self.Name, self.S_birth.Name, self.N_birth
        return 'Cohort({}, Birth:{}, NBir:{})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        s_death = model.DCore.States[kwargs['s_death']]
        model.Behaviours[name] = BirthListener(name, s_death)

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.N_birth

    def match(self, be_src, ags_src, ags_new, ti):
        self.N_birth = be_src.N_birth
