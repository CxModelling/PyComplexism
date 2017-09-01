from dzdy.abmodel import AgentBasedModel, MetaABM, install_behaviour, install_network, install_trait
from dzdy.mcore import AbsBlueprintMCore
from copy import deepcopy
from collections import OrderedDict

__author__ = 'TimeWz667'


class BlueprintABM(AbsBlueprintMCore):
    def __init__(self, name, tar_pc, tar_dc):
        self.Name = name
        self.TargetedCore = tar_pc, tar_dc
        self.Networks = dict()
        self.Behaviours = OrderedDict()
        self.Traits = dict()
        self.Obs_s_t_b = list(), list(), list()

    @property
    def TargetedPCore(self):
        return self.TargetedCore[0]

    @property
    def TargetedDCore(self):
        return self.TargetedCore[1]

    def add_network(self, net_name, net_type, **kwargs):
        if net_name in self.Networks:
            return
        self.Networks[net_name] = {'Type': net_type, 'Args': dict(kwargs)}

    def add_trait(self, trt_name, trt_type, **kwargs):
        self.Traits[trt_name] = {'Type': trt_type, 'Args': dict(kwargs)}

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

    def generate(self, name, **kwargs):
        pc, dc = kwargs['pc'], kwargs['dc'],
        ag_prefix = kwargs['ag_prefix'] if 'ag_prefix' in kwargs else 'Ag'
        meta = MetaABM(self.TargetedPCore, self.TargetedDCore, self.Name)
        mod = AgentBasedModel(name, dc, pc, meta, ag_prefix=ag_prefix)
        for k, v in self.Traits.items():
            install_trait(mod, k, v['Type'], v['Args'])
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

    def clone(self, mod_src, **kwargs):
        # copy model structure
        pc_new = kwargs['pc'] if 'pc' in kwargs else mod_src.PCore
        dc_new = kwargs['dc'] if 'dc' in kwargs else mod_src.DCore

        tr_tte = kwargs['tr_tte'] if 'tr_tte' in kwargs else True

        mod_new = self.generate(mod_src.Name, pc=pc_new, dc=dc_new)

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
        js['BehaviourOrder'] = list(self.Behaviours.keys())
        js['Traits'] = self.Traits
        js['Observation'] = {k: v for k, v in zip(['State', 'Transition', 'Behaviour'],self.Obs_s_t_b)}

        return js

    @staticmethod
    def from_json(js):
        bp = BlueprintABM(js['Name'], js['TargetedPCore'], js['TargetedDCore'])
        bp.Networks = deepcopy(js['Networks'])
        bes = deepcopy(js['Behaviours'])
        beo = js['BehaviourOrder']
        for k in beo:
            bp.Behaviours[k] = bes[k]
        bp.Traits = deepcopy(js['Traits'])
        obs = js['Observation']
        bp.set_observations(obs['State'], obs['Transition'], obs['Behaviour'])
        return bp
