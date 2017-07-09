from dzdy.abmodel import AgentBasedModel, MetaABM, install_behaviour, install_network
from copy import deepcopy

__author__ = 'TimeWz667'


class BlueprintABM:
    def __init__(self, name, tar_pc, tar_dc):
        self.Name = name
        self.TargetedPCore = tar_pc
        self.TargetedDCore = tar_dc

        self.Networks = dict()
        self.Behaviours = dict()
        self.FillUps = list()
        self.Obs_s_t_b = None, None, None

    def add_network(self, net_name, net_type, **kwargs):
        if net_name in self.Networks:
            return
        self.Networks[net_name] = {'Type': net_type, 'Args': dict(kwargs)}

    def add_fill_up(self, fu_type, **kwargs):
        fu = {'Type': fu_type}
        fu.update(kwargs)
        self.FillUps.append(fu)

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

    def generate(self, name, pc, dc, ag_prefix='Ag'):
        meta = MetaABM(self.TargetedPCore, self.TargetedDCore, self.Name)
        mod = AgentBasedModel(name, dc, pc, meta, ag_prefix=ag_prefix)
        for fi in self.FillUps:
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

    def clone(self, mod_src, pc=None, dc=None, tr_tte=True):
        # copy model structure
        pc_new = pc if pc else mod_src.PCore
        dc_new = dc if dc else mod_src.DCore

        mod_new = self.generate(mod_src.Name, pc_new, dc_new)

        time_copy = mod_src.TimeEnd if mod_src.TimeEnd else 0
        mod_new.TimeEnd = mod_src.TimeEnd

        trs = dc_new.Transitions
        ags_src = mod_src.Pop.Agents

        # copy agents
        if tr_tte:
            trs_src = mod_src.DCore.Transitions
            tr_ch = [k for k, v in trs.items() if str(trs_src[k]) != str(v)]
            for k, v in ags_src.items():
                mod_new.Pop.Agents[k] = v.clone(dc_new, tr_ch)
        else:
            for k, v in ags_src.items():
                mod_new.Pop.Agents[k] = v.clone(dc_new)

        # rebuild population and networks
        mod_new.Pop.Eve.Last = mod_src.Pop.Eve.Last

        ags_new = mod_new.Pop.Agents
        mod_new.Pop.Networks.match(mod_src.Pop.Networks, ags_new)

        # rebuild behaviours and modifiers
        for be_src, be_new in zip(mod_src.Behaviours.values(), mod_new.Behaviours.values()):
            be_new.match(be_src, ags_src, ags_new, time_copy)

        for ag in mod_new.agents:
            ag.update(time_copy)

        mod_new.Obs.TimeSeries = mod_src.Obs.TimeSeries.copy()

        return mod_new

    def to_json(self):
        js = dict()
        js['Name'] = self.Name
        js['Type'] = 'ABN'
        js['TargetedPCore'] = self.TargetedPCore
        js['TargetedDCore'] = self.TargetedDCore
        js['Networks'] = self.Networks
        js['Behaviours'] = self.Behaviours
        js['FillUps'] = self.FillUps
        js['Observation'] = {k: v for k, v in zip(['State', 'Transition', 'Behaviour'],self.Obs_s_t_b)}

        return js

    @staticmethod
    def from_json(js):
        bp = BlueprintABM(js['Name'], js['TargetedPCore'], js['TargetedDCore'])
        bp.Networks = deepcopy(js['Networks'])
        bp.Behaviours = deepcopy(js['Behaviours'])
        bp.FillUps = deepcopy(js['FillUps'])
        obs = js['Observation']
        bp.set_observations(obs['State'], obs['Transition'], obs['Behaviour'])
        return bp
