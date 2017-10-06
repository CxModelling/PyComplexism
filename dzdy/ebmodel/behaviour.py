from abc import ABCMeta, abstractmethod, abstractstaticmethod
__author__ = 'TimeWz667'


class Behaviour(metaclass=ABCMeta):
    def __init__(self, name, target=None):
        self.Name = name
        self.Target = target

    @abstractmethod
    def initialise(self, model, core, ti):
        pass

    def modify(self, rate, core, ys, ti):
        return rate

    def modify_in(self, ins, core, ti):
        return ins

    def modify_out(self, outs, core, ti):
        return outs

    @abstractmethod
    def fill(self, obs, model, ti):
        pass  # obs['B.{}'.format(self.Name)] = self.Value

    @abstractmethod
    def to_json(self):
        pass

    @abstractstaticmethod
    def from_json(self, js):
        pass


class Multiplier(Behaviour):
    def __init__(self, name, t_tar):
        Behaviour.__init__(self, name, t_tar)
        self.Value = 0

    def initialise(self, model, core, ti):
        pass

    def __repr__(self):
        return 'Multiplier({} on {} by {})'.format(self.Name, self.Target, self.Value)

    def modify(self, rate, core, ys, ti):
        return rate * self.Value

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value

    def to_json(self):
        return {'Name': self.Name,
                'Type': 'Multiplier',
                't_tar': self.Target,
                'Value': self.Value}

    def from_json(self, js):
        be = Multiplier(js['Name'], js['t_tar'])
        be.Value = js['Value']
        return be


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

    def modify(self, rate, core, ys, ti):
        n = sum(ys)
        s = core.count_st_ys(self.Src, ys)
        self.Value = s/n
        return rate * self.Value

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value

    def to_json(self):
        return {'Name': self.Name,
                'Type': 'InfectionFD',
                't_tar': self.Target,
                's_src': self.Src,
                'Value': self.Value}

    def from_json(self, js):
        be = InfectionFD(js['Name'], js['t_tar'], js['s_src'])
        be.Value = js['Value']
        return be


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

    def modify(self, rate, core, ys, ti):
        s = core.count_st_ys(self.Src, ys)
        self.Value = s
        return rate * self.Value

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value

    def to_json(self):
        return {'Name': self.Name,
                'Type': 'InfectionDD',
                't_tar': self.Target,
                's_src': self.Src,
                'Value': self.Value}

    def from_json(self, js):
        be = InfectionDD(js['Name'], js['t_tar'], js['s_src'])
        be.Value = js['Value']
        return be


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

    def modify_in(self, ins, model, ti):
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
        obs[self.Name] = self.Value

    def to_json(self):
        return {'Name': self.Name,
                'Type': 'Cohort',
                's_death': self.Death,
                'Value': self.Value,
                'IndexDeath': list(self.IndexDeath)}

    def from_json(self, js):
        be = Cohort(js['Name'], js['s_death'])
        be.Value = js['Value']
        if 'IndexDeath' in js:
            be.IndexDeath = list(js['IndexDeath'])
        return be


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

    def modify_in(self, ins, model, ti):
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
        obs[self.Name] = self.Value

    def to_json(self):
        return {'Name': self.Name,
                'Type': 'Reincarnation',
                's_death': self.Death,
                's_birth': self.Birth,
                'Value': self.Value,
                'IndexDeath': list(self.IndexDeath)}

    def from_json(self, js):
        be = Reincarnation(js['Name'], js['s_death'], js['s_birth'])
        be.Value = js['Value']
        if 'IndexDeath' in js:
            be.IndexDeath = list(js['IndexDeath'])
        return be


class PopDynamic(Behaviour):
    def __init__(self, name, s_birth, s_death, rate_birth, rate_death):
        Behaviour.__init__(self, name, None)
        self.Value = 0
        self.Death = s_death
        self.Birth = s_birth
        self.IndexDeath = None
        self.RateBirth = rate_birth
        self.RateDeath = rate_death

    def __repr__(self):
        return 'PopDynamic'

    def initialise(self, model, core, ti):
        dead = core.find_states(self.Death)
        self.IndexDeath = [i for i, v in enumerate(dead) if v]

    def modify_in(self, ins, model, ti):
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
        obs[self.Name] = self.Value

    def to_json(self):
        return {'Name': self.Name,
                'Type': 'Reincarnation',
                's_death': self.Death,
                's_birth': self.Birth,
                'Value': self.Value,
                'IndexDeath': list(self.IndexDeath)}

    def from_json(self, js):
        be = Reincarnation(js['Name'], js['s_death'], js['s_birth'])
        be.Value = js['Value']
        if 'IndexDeath' in js:
            be.IndexDeath = list(js['IndexDeath'])
        return be


class DemoDynamic(Behaviour):
    def __init__(self, name, s_birth, s_death, t_death, demo):
        Behaviour.__init__(self, name, t_death)
        self.Value = 0
        self.Death = s_death
        self.Birth = s_birth
        self.Demo = demo
        self.IndexDeath = None

    def __repr__(self):
        return 'DemoDynamic'

    def initialise(self, model, core, ti):
        dead = core.find_states(self.Death)
        self.IndexDeath = [i for i, v in enumerate(dead) if v]

    def modify_in(self, ins, model, ti):
        res = [flow for flow in ins if flow[1] not in self.IndexDeath]
        bir = self.Demo.RateBirth(ti) * sum(model.Ys.values())
        res.append(model.compose_incidence(None, self.Birth, 'Birth', bir))
        return res

    def modify(self, rate, core, ys, ti):
        self.Value = self.Demo.RateDeath(ti)
        return rate * self.Value

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value

    def to_json(self):
        return {'Name': self.Name,
                'Type': 'Reincarnation',
                's_death': self.Death,
                's_birth': self.Birth,
                'Value': self.Value,
                'IndexDeath': list(self.IndexDeath)}

    def from_json(self, js):
        be = Reincarnation(js['Name'], js['s_death'], js['s_birth'])
        be.Value = js['Value']
        if 'IndexDeath' in js:
            be.IndexDeath = list(js['IndexDeath'])
        return be

