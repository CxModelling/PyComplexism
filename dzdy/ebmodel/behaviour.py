from abc import ABCMeta, abstractmethod
__author__ = 'TimeWz667'


class Behaviour(metaclass=ABCMeta):
    def __init__(self, name, target=None):
        self.Name = name
        self.Target = target

    @abstractmethod
    def initialise(self, model, core, ti):
        pass

    def modify(self, rate, core, ys, t):
        return rate

    def modify_in(self, ins, core, t):
        return ins

    def modify_out(self, outs, core, t):
        return outs

    @abstractmethod
    def fill(self, obs, model, ti):
        pass # obs['B.{}'.format(self.Name)] = self.Value


class Multiplier(Behaviour):
    def __init__(self, name, t_tar):
        Behaviour.__init__(self, name, t_tar)
        self.Value = 0

    def initialise(self, model, core, ti):
        pass

    def __repr__(self):
        return 'Multiplier({} on {} by {})'.format(self.Name, self.Target, self.Value)

    def modify(self, rate, core, ys, t):
        return rate * self.Value

    def fill(self, obs, model, ti):
        pass


class InfectionFD(Behaviour):
    def __init__(self, name, t_tar, s_src):
        Behaviour.__init__(self, name, t_tar)
        self.Value = 0
        self.Src = s_src

    def __repr__(self):
        return 'InfectionFD({} on {} by {})'.format(self.Name, self.Target, self.Value)

    def initialise(self, model, core, ti):
        ys = model.Y
        n = sum(ys)
        s = core.count_st_ys(self.Src, ys)
        self.Value = s / n

    def modify(self, rate, core, ys, t):
        n = sum(ys)
        s = core.count_st_ys(self.Src, ys)
        self.Value = s/n
        return rate * self.Value

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.Value


class InfectionDD(Behaviour):
    def __init__(self, name, t_tar, s_src):
        Behaviour.__init__(self, name, t_tar)
        self.Value = 0
        self.Src = s_src

    def __repr__(self):
        return 'InfectionDD({} on {} by {})'.format(self.Name, self.Target, self.Value)

    def initialise(self, model, core, ti):
        s = core.count_st_ys(self.Src, model.Y)
        self.Value = s

    def modify(self, rate, core, ys, t):
        s = core.count_st_ys(self.Src, ys)
        self.Value = s
        return rate * self.Value

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.Value


class Cohort(Behaviour):
    def __init__(self, name, s_death):
        Behaviour.__init__(self, name, None)
        self.Value = 0
        self.Death = s_death
        self.IndexDeath = None

    def __repr__(self):
        return 'Cohort({} on {})'.format(self.Name, self.Target)

    def initialise(self, model, core, ti):
        dead = core.find_states(self.Death)
        self.IndexDeath = [i for i, v in enumerate(dead) if v]

    def modify_in(self, ins, model, t):
        dea = 0
        res = list()
        for flow in ins:
            if flow[1] in self.IndexDeath:
                dea += flow[3]
            else:
                res.append(flow)
        self.Value = dea
        return res

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.Value


class Reincarnation(Behaviour):
    def __init__(self, name, s_birth, s_death):
        Behaviour.__init__(self, name, None)
        self.Value = 0
        self.Death = s_death
        self.Birth = s_birth
        self.IndexDeath = None

    def __repr__(self):
        return 'Reincarnation({} on {})'.format(self.Name, self.Target)

    def initialise(self, model, core, ti):
        dead = core.find_states(self.Death)
        self.IndexDeath = [i for i, v in enumerate(dead) if v]

    def modify_in(self, ins, model, t):
        dea = 0
        res = list()
        for flow in ins:
            if flow[1] in self.IndexDeath:
                dea += flow[3]
            else:
                res.append(flow)
        self.Value = dea

        res.append(model.compose_incidence(None, self.Birth, 'Birth', self.Value))
        return res

    def fill(self, obs, model, ti):
        obs['B.{}'.format(self.Name)] = self.Value
