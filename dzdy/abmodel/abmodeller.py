from dzdy.mcore import AbsDirector
from dzdy.abmodel import AgentBasedModel, install_behaviour, install_network
__author__ = 'TimeWz667'


class AgentBasedModelBluePrint:
    def __init__(self, tar_pc, tar_dc):
        self.TargetedPCore = tar_pc
        self.TargetedDCore = tar_dc

        self.Networks = dict()
        self.Behaviours = dict()
        self.FillUp = list()
        self.Obs_s_t_b = None, None, None

    def add_network(self, net_name, net_type, **kwargs):
        if net_name in self.Networks:
            return
        self.Networks[net_name] = {'Type': net_type, 'Args': dict(kwargs)}

    def add_fill_up(self, fu_type, **kwargs):
        fu = {'Type': fu_type}
        fu.update(kwargs)
        self.FillUp.append(fu)

    def add_behaviour(self, be_name, be_type, **kwargs):
        if be_name in self.Behaviours:
            return
        self.Behaviours[be_name] = {'Type': be_type, 'Args': dict(kwargs)}

    def set_observations(self, states=None, transitions=None, behaviours=None):
        s, t, b = self.Obs_s_t_b
        s = states if states else s
        t = transitions if transitions else t
        b = behaviours if behaviours else b
        self.Obs_s_t_b = s, t, b

    def generate(self, name, pc, dc):
        mod = AgentBasedModel(name, dc, pc)
        for fi in self.FillUp:
            mod.Pop.append_fill_json(fi)
        for k, v in self.Behaviours.items():
            install_behaviour(mod, k, v['Type'], v['Args'])
        for k, v in self.Networks.items():
            install_network(mod, k, v['Type'], v['Args'])
        sts, trs, bes = self.Obs_s_t_b
        if sts:
            for st in sts:
                mod.add_obs_st(st)
        if trs:
            for tr in trs:
                mod.add_obs_tr(tr)
        if bes:
            for be in bes:
                mod.add_obs_be(be)
        return mod


class AgentBasedModeller(AbsDirector):

    def freeze(self, mod):
        pass

    def defrost(self, js):
        pass

    def clone(self, mod, pc):
        pass
