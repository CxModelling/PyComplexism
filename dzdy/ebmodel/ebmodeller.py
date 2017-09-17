from dzdy.ebmodel import *
from dzdy.mcore import AbsBlueprintMCore
from copy import deepcopy

__author__ = 'TimeWz667'


class BlueprintCoreODE(AbsBlueprintMCore):
    def __init__(self, name, tar_pc, tar_dc):
        AbsBlueprintMCore.__init__(self, name, {'dt': 1, 'fdt': 0.1})
        self.TargetedCore = tar_pc, tar_dc
        self.Behaviours = list()
        self.Obs_s_t_b = list(), list(), list()

    @property
    def TargetedPCore(self):
        return self.TargetedCore[0]

    @property
    def TargetedDCore(self):
        return self.TargetedCore[1]

    def add_behaviour(self, be_name, be_type, **kwargs):
        if be_name in self.Behaviours:
            return
        self.Behaviours.append({'Name': be_name,
                                'Type': be_type,
                                'Args': dict(kwargs)})

    def set_observations(self, states=None, transitions=None, behaviours=None):
        s, t, b = self.Obs_s_t_b
        s = states if states else s
        t = transitions if transitions else t
        b = behaviours if behaviours else b
        self.Obs_s_t_b = s, t, b

    def generate(self, name, **kwargs):
        pc, dc = kwargs['pc'], kwargs['dc'],
        meta = MetaCoreEBM(self.TargetedPCore, self.TargetedDCore, self.Name)
        mc = CoreODE(dc)
        mod = ODEModel(name, mc, meta, **self.Arguments)

        for be in self.Behaviours:
            install_behaviour(mod, be['Name'], be['Type'], be['Args'])

        sts, trs, bes = self.Obs_s_t_b
        if sts:
            for st in sts:
                mod.add_obs_state(st)
        if trs:
            for tr in trs:
                mod.add_obs_transition(tr)
        if bes:
            for be in bes:
                mod.add_obs_behaviour(be)
        return mod

    def clone(self, mod_src, **kwargs):
        # copy model structure
        dc_new = kwargs['dc'] if 'dc' in kwargs else mod_src.DCore

        mod_new = mod_src.clone(dc_new)
        mod_new.Obs.TimeSeries = mod_src.Obs.TimeSeries.copy()

        return mod_new

    def to_json(self):
        js = dict()
        js['Name'] = self.Name
        js['Arguments'] = self.Arguments
        js['Type'] = 'CoreODE'
        js['TargetedPCore'] = self.TargetedPCore
        js['TargetedDCore'] = self.TargetedDCore
        js['Behaviours'] = self.Behaviours
        js['Observation'] = {k: v for k, v in zip(['State', 'Transition', 'Behaviour'],self.Obs_s_t_b)}

        return js

    @staticmethod
    def from_json(js):
        bp = BlueprintCoreODE(js['Name'], js['TargetedPCore'], js['TargetedDCore'])
        for k, v in js['Arguments']:
            bp.set_arguments(k, v)
        bp.Behaviours = deepcopy(js['Behaviours'])
        obs = js['Observation']
        bp.set_observations(obs['State'], obs['Transition'], obs['Behaviour'])
        return bp
