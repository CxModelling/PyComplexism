from complexism.agentbased import AgentBasedModel, MetaABM
from complexism.mcore import AbsBlueprintMCore
from copy import deepcopy
from epidag.factory import get_workshop
import logging


__author__ = 'TimeWz667'

__all__ = ['BlueprintABM', 'install_behaviour', 'install_network', 'install_trait']

logger = logging.getLogger('__name__')


class BlueprintABM(AbsBlueprintMCore):
    def __init__(self, name, tar_pc, tar_dc):
        AbsBlueprintMCore.__init__(self, name, {'ag_prefix': 'Ag'}, pc=tar_pc, dc=tar_dc)
        self.Networks = list()
        self.Behaviours = list()
        self.Traits = list()
        self.Obs_s_t_b = list(), list(), list()

    def add_network(self, net_name, net_type, **kwargs):
        self.Networks.append({
            'Name': net_name,
            'Type': net_type,
            'Args': dict(kwargs)
        })

    def add_network_json(self, js):
        self.Networks.append(js)

    def add_behaviour(self, be_name, be_type, **kwargs):
        self.Behaviours.append({"Name": be_name, 'Type': be_type, 'Args': dict(kwargs)})

    def set_observations(self, states=None, transitions=None, behaviours=None):
        s, t, b = self.Obs_s_t_b
        s = states if states else s
        t = transitions if transitions else t
        b = behaviours if behaviours else b
        self.Obs_s_t_b = s, t, b

    def generate(self, name, **kwargs):
        pc, dc = kwargs['pc'], kwargs['dc'],
        meta = MetaABM(self.TargetedPCore, self.TargetedDCore, self.Name)
        mod = AgentBasedModel(name, dc, pc, meta, **self.Arguments)

        resources = {
            'states': dc.States,
            'transitions': dc.Transitions,
            'networks': [net[0] for net in self.Networks],
            'traits': [trt[0] for trt in self.Traits]
        }
        resources.update(pc.Locus)
        # lock

        ws = get_workshop('ABM_BE')
        ws.renew_resources(resources)
        for be in self.Behaviours:
            be = ws.create(be, logger=logger)
            mod.add_behaviour(be)
        ws.clear_resources()

        ws = get_workshop('Traits')
        ws.renew_resources(resources)
        for trt in self.Traits:
            trt = ws.create(trt, logger=logger)
            mod.add_trait(trt)
        ws.clear_resources()

        ws = get_workshop('Networks')
        ws.renew_resources(resources)
        for net in self.Networks:
            net = ws.create(net, logger=logger)
            mod.add_trait(net)
        ws.clear_resources()

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
        js['Arguments'] = self.Arguments
        js['Type'] = 'ABM'
        js['TargetedPCore'] = self.TargetedPCore
        js['TargetedDCore'] = self.TargetedDCore
        js['Networks'] = self.Networks
        js['Behaviours'] = self.Behaviours
        js['Traits'] = self.Traits
        js['Observation'] = {k: v for k, v in zip(['State', 'Transition', 'Behaviour'], self.Obs_s_t_b)}

        return js

    @staticmethod
    def from_json(js):
        bp = BlueprintABM(js['Name'], js['TargetedPCore'], js['TargetedDCore'])
        for k, v in js['Arguments']:
            bp.set_arguments(k, v)
        bp.Networks = deepcopy(js['Networks'])
        bes = deepcopy(js['Behaviours'])
        beo = js['BehaviourOrder']
        for k in beo:
            bp.Behaviours[k] = bes[k]
        bp.Traits = deepcopy(js['Traits'])
        obs = js['Observation']
        bp.set_observations(obs['State'], obs['Transition'], obs['Behaviour'])
        return bp


def form_resources(abm):
    pc, dc = abm.PCore, abm.DCore
    resources = {
        'states': dc.States,
        'transitions': dc.Transitions,
        'networks': abm.Pop.Networks.list(),
        'traits': abm.Pop.Eve.Traits.list()
    }
    resources.update(pc.Locus)
    return resources


def install_behaviour(abm, be_name, be_type, log=None, **kwargs):
    js = {'Name': be_name, 'Type': be_type, 'Args': dict(kwargs)}
    ws = get_workshop('ABM_BE')
    ws.renew_resources(form_resources(abm))
    if ws.validate(js, logger=log):
        be = ws.create(js, logger=log)
        abm.add_behaviour(be)
    ws.clear_resources()


def install_network(abm, net_name, net_type, log=None, **kwargs):
    js = {'Name': net_name, 'Type': net_type, 'Args': dict(kwargs)}
    ws = get_workshop('Networks')
    ws.renew_resources(form_resources(abm))
    if ws.validate(js, logger=log):
        net = ws.create(js, logger=log)
        abm.add_network(net)
    ws.clear_resources()
