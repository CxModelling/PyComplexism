from complexism.agentbased import ForeignTrigger, TimeIndBehaviour
from .behaviour import PassiveModBehaviour
from ..modifier import GloRateModifier

__author__ = 'TimeWz667'
__all__ = ['ForeignShock', 'Immigration']


class ForeignShock(TimeIndModBehaviour):
    def __init__(self, name, t_tar, mod_src=None, msg=None, par_src=None, default=1):
        trigger = ForeignTrigger(model=mod_src, msg=msg)
        mod = GloRateModifier(name, t_tar)
        TimeIndModBehaviour.__init__(self, name, mod, trigger)
        self.Model = mod_src
        self.Source = par_src
        self.T_tar = t_tar.Name
        self.Default = default
        self.Value = self.Default

    def set_source(self, mod_src, msg, par_src):
        self.Model = mod_src
        self.Source = par_src
        self.Trigger.add_source(mod_src, msg)

    def initialise(self, model, ti):
        self.Value = self.Default
        self.ProtoModifier.Value = self.Value

    def impulse_foreign(self, model, fore, message, ti, **kwargs):
        self.Value = fore.get_snapshot(self.Source, ti)
        # print(self.Value, ti)
        if self.Value is None:
            self.Value = self.Default
        self.ProtoModifier.Value = self.Value
        for ag in model.agents:
            ag.modify(self.Name, ti)

    @staticmethod
    def decorate(name, model, **kwargs):
        mod_src = kwargs['mod_src'] if 'mod_src' in kwargs else None
        par_src = kwargs['par_src'] if 'par_src' in kwargs else None
        message = kwargs['msg'] if 'msg' in kwargs else None
        t_tar = model.DCore.Transitions[kwargs['t_tar']]
        default = kwargs['default'] if 'default' in kwargs else 1
        model.Behaviours[name] = ForeignShock(name, t_tar, mod_src, message, par_src, default)

    def __repr__(self):
        opt = self.Name, '{}@{}'.format(self.Model, self.Source), self.T_tar, self.Value
        return 'Foreign({}, From ={}, To={}, Value={})'.format(*opt)

    def match(self, be_src, ags_src, ags_new, ti):
        self.Value = be_src.Value
        for ag in ags_new.values():
            self.register(ag, ti)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value


# class ForeignSumShock(TimeIndModBehaviour):
#     def __init__(self, name, mod_par_src, t_tar, default):
#         tri = ForeignSetTrigger(mps=mod_par_src)
#         mod = GloRateModifier(name, t_tar)
#         TimeIndModBehaviour.__init__(self, name, mod, tri)
#         self.Models = dict(mod_par_src)
#         self.T_tar = t_tar.Name
#         self.Default = default
#         self.Values = {k: self.Default for k in self.Models.keys()}
#
#     def set_source(self, mod_src, par_src):
#         self.Trigger.append(mod_src, par_src)
#         self.Models[mod_src] = par_src
#         self.Values[mod_src] = self.Default
#
#     def initialise(self, model, ti):
#         self.Values = {k: self.Default for k, v in self.Values.items()}
#         self.ProtoModifier.Value = sum(self.Values.values())
#
#     def impulse_foreign(self, model, fore, message, ti, **kwargs):
#         key = fore.Name
#         value = fore[self.Models[key]]
#         self.Values[key] = value
#         self.ProtoModifier.Value = sum(self.Values.values())
#         for ag in model.agents:
#             ag.modify(self.Name, ti)
#
#     @staticmethod
#     def decorate(name, model, **kwargs):
#         mod_par_src = kwargs['mod_par_src'] if 'mod_par_src' not in kwargs else dict()
#         t_tar = model.DCore.Transitions[kwargs['t_tar']]
#         default = kwargs['default'] if 'default' not in kwargs else 1
#         model.Behaviours[name] = ForeignSumShock(name, mod_par_src, t_tar, default)
#
#     def match(self, be_src, ags_src, ags_new, ti):
#         self.Models = dict(be_src.Models)
#         self.Values = dict(be_src.Value)
#         self.ProtoModifier.Value = sum(self.Values.values())
#         for ag in ags_new.values():
#             self.register(ag, ti)
#
#     def __repr__(self):
#         opt = self.Name, self.T_tar, sum(self.Values.values())
#         return 'Foreign({}, To={}, Value={})'.format(*opt)
#
#     def fill(self, obs, model, ti):
#         obs[self.Name] = sum(self.Values.values())


class Immigration(TimeIndBehaviour):
    def __init__(self, name, mod_src=None, message=None, par_src=None, s_immigrant=None):
        trigger = ForeignTrigger(model=None, msg=par_src)
        TimeIndBehaviour.__init__(self, name, trigger)
        self.Model = mod_src
        self.Source = par_src
        self.S_immigrant = s_immigrant
        self.ImN = 0

    def set_source(self, mod_src, message, par_src):
        self.Model = mod_src
        self.Source = par_src
        loc = message if message != 'update' else None  # todo
        self.Trigger.add_source(mod_src, loc)

    def initialise(self, model, ti):
        self.ImN = 0

    def register(self, ag, ti):
        pass

    def impulse_foreign(self, model, fore, message, ti, **kwargs):
        if message == self.Source:
            model.birth(n=1, ti=ti, st=self.S_immigrant.Name)
            self.ImN += 1
        return self.Name

    @staticmethod
    def decorate(name, model, **kwargs):
        mod_src = kwargs['mod_src'] if 'mod_src' in kwargs else None
        par_src = kwargs['par_src'] if 'par_src' in kwargs else None
        message = kwargs['message'] if 'message' in kwargs else None
        s_immigrant = model.DCore.States[kwargs['s_immigrant']]
        model.Behaviours[name] = Immigration(name, mod_src, message, par_src, s_immigrant)

    def match(self, be_src, ags_src, ags_new, ti):
        self.ImN = be_src.ImN

    def __repr__(self):
        opt = self.Name, '{}@{}'.format(self.Model, self.Source), self.ImN
        return 'Immigration({}, From ={}, Value={})'.format(*opt)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.ImN
        return obs
