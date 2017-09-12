from dzdy.abmodel.behaviour import *
from dzdy.abmodel.modifier import *
__author__ = 'TimeWz667'


class ForeignShock(ModBe):
    def __init__(self, name, mod_src, par_src, t_tar):
        tri = ForeignTrigger(mod_src, par_src)
        mod = GloRateModifier(name, t_tar)
        ModBe.__init__(self, name, mod, tri)
        self.Source = mod_src, par_src
        self.Target = t_tar.Name
        self.Val = 0

    def initialise(self, model, ti):
        self.shock(model, ti)

    def impulse_foreign(self, model, fore, ti):
        self.Val = fore[self.Source[1]]
        self.shock(model, ti)

    def shock(self, model, ti):
        self.ModPrototype.Val = self.Val
        for ag in model.agents:
            ag.modify(self.Name, ti)

    def __repr__(self):
        opt = self.Name, '{}:{}'.format(*self.Source), self.Target, self.Val
        return 'Foreign({}, {} on {}, Value={})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        target = model.DCore.Transitions[kwargs['t_tar']]
        model.Behaviours[name] = ForeignShock(name, kwargs['mod_src'], kwargs['par_src'], target)

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.Val
        return obs

    def match(self, be_src, ags_src, ags_new, ti):
        self.Val = be_src.Val
        for ag_new, ag_src in zip(ags_new.values(), ags_src.values()):
            self.register(ag_new, ti)
            ag_new.Mods[self.Name].Val = ag_src.Mods[self.Name].Val


class ForeignAddShock(ModBe):
    def __init__(self, name, src_value, src_target):
        tri = ForeignSetTrigger(src_value)
        mod = GloRateModifier(name, src_target)
        ModBe.__init__(self, name, mod, tri)
        self.Source = src_value
        self.Target = src_target.Name
        self.Values = dict()
        self.Sum = 0

    def append_foreign(self, mod):
        """

        Args:
            mod: name of foreign model

        """
        self.Trigger.append(mod)
        self.Values[mod] = 0

    def initialise(self, model, ti):
        self.shock(model, ti)

    def impulse_foreign(self, model, fore, ti):
        self.Values[fore.Name] = fore[self.Source]
        self.shock(model, ti)

    def shock(self, model, ti):
        self.ModPrototype.Val = self.Sum =  sum(self.Values.values())
        for ag in model.agents:
            ag.modify(self.Name, ti)

    def __repr__(self):
        opt = self.Name, '{}:{}'.format(*self.Source), self.Target, self.Sum
        return 'Foreign({}, {} on {}, Value={})'.format(*opt)

    @staticmethod
    def decorate(name, model, **kwargs):
        target = model.DCore.Transitions[kwargs['src_target']]
        m = ForeignAddShock(name, kwargs['src_value'], target)
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
        obs['B.{}'.format(self.Name)] = self.N_dead

    def match(self, be_src, ags_src, ags_new, ti):
        self.N_dead = be_src.N_dead