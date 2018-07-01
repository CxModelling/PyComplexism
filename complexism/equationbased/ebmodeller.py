from complexism.mcore import AbsBlueprintMCore
from inspect import signature
import epidag as dag
from copy import deepcopy
from .odeebm import OrdinaryDifferentialEquationModel

__author__ = 'TimeWz667'


class BlueprintODEEBM(AbsBlueprintMCore):
    def __init__(self, name):
        AbsBlueprintMCore.__init__(self, name)
        self.DT = 0.1
        self.ObsDT = 1
        self.ODE = None
        self.Ys = None
        self.Xs = None
        self.ObsYs = None
        self.Measurements = list()
        self.ObsStocks = list()

    def set_fn_ode(self, fn, ys):
        for x, y in zip(signature(fn).parameters.keys(), ['y', 't', 'p', 'x']):
            if x != y:
                raise TypeError('Positional arguments should be y, t, p, and x')
        self.ODE = fn
        self.Ys = list(ys)

    def set_external_variables(self, xs):
        self.Xs = dict(xs)

    def add_observing_function(self, fn):
        for x, y in zip(signature(fn).parameters.keys(), ['y', 't', 'p', 'x']):
            if x != y:
                raise TypeError('Positional arguments should be y, t, p, and x')
        self.Measurements.append(fn)

    def set_observations(self, stocks='*'):
        if stocks == '*':
            self.ObsYs = list(self.Ys)
        elif isinstance(stocks, list):
            self.ObsYs = [s for s in stocks if s in self.Ys]

    def set_dt(self, dt=0.1, odt=1):
        if dt <= 0 or odt <=0:
            raise ValueError('Time differences must be positive numbers')
        dt = min(dt, odt)
        self.DT, self.ObsDT = dt, odt

    def get_parameter_hierarchy(self, **kwargs):
        return {

        }

    def generate(self, name, **kwargs):
        if not all([self.Ys, self.ODE, self.ObsYs]):
            raise TypeError('Equation have not been assigned')

        # Prepare PC
        if 'pc' in kwargs:
            pc = kwargs['pc']
        elif 'sm' in kwargs:
            sm = kwargs['sm']
            pc = sm.generate(name, exo=kwargs['exo'] if 'exo' in kwargs else None)
        elif 'bn' in kwargs:
            bn = kwargs['bn']
            random = kwargs['random'] if 'random' in kwargs else []
            hie = kwargs['hie'] if 'hie' in kwargs else self.get_parameter_hierarchy()
            sm = dag.as_simulation_core(bn, hie=hie, random=random)
            pc = sm.generate(name, exo=kwargs['exo'] if 'exo' in kwargs else None)
        else:
            raise KeyError('Parameter core not found')

        model = OrdinaryDifferentialEquationModel(name, self.ODE, self.DT, self.ObsDT,
                                                  ys=self.Ys, xs=self.Xs, env=pc)

        # Assign observations
        for st in self.ObsYs:
            model.add_observing_stock(st)

        for fn in self.Measurements:
            model.add_observing_function(fn)

        return model

    def to_json(self):
        pass

    def clone(self, mod_src, **kwargs):
        pass

    def from_json(self, js):
        pass

#
# class BlueprintCoreODE(AbsBlueprintMCore):
#     def __init__(self, name, tar_pc, tar_dc):
#         AbsBlueprintMCore.__init__(self, name, {'dt': 1, 'fdt': 0.1}, pc=tar_pc, dc=tar_dc)
#         self.Behaviours = list()
#         self.Obs_s_t_b = list(), list(), list()
#
#     def add_behaviour(self, be_name, be_type, **kwargs):
#         if be_name in self.Behaviours:
#             return
#         self.Behaviours.append({'Name': be_name,
#                                 'Type': be_type,
#                                 'Args': dict(kwargs)})
#
#     def set_observations(self, states=None, transitions=None, behaviours=None):
#         s, t, b = self.Obs_s_t_b
#         s = states if states else s
#         t = transitions if transitions else t
#         b = behaviours if behaviours else b
#         self.Obs_s_t_b = s, t, b
#
#     def generate(self, name, logger=None, **kwargs):
#         pc, dc = kwargs['pc'], kwargs['dc'],
#         meta = MetaCoreEBM(self.TargetedPCore, self.TargetedDCore, self.Name)
#         mc = CoreODE(dc)
#         mod = ODEModel(name, mc, pc=pc, meta=meta, **self.Arguments)
#
#         ws = get_workshop('EBM_BE')
#         resources = {
#             'states': list(dc.States.keys()),
#             'transitions': list(dc.Transitions.keys())
#         }
#         resources.update(pc.Locus)
#         # lock
#         ws.renew_resources(resources)
#
#         for be in self.Behaviours:
#             mod.ODE.add_behaviour(ws.create(be, logger=logger))
#
#         ws.clear_resources()
#         # release
#         sts, trs, bes = self.Obs_s_t_b
#         if sts:
#             for st in sts:
#                 mod.add_obs_state(st)
#         if trs:
#             for tr in trs:
#                 mod.add_obs_transition(tr)
#         if bes:
#             for be in bes:
#                 mod.add_obs_behaviour(be)
#         return mod
#
#     def clone(self, mod_src, **kwargs):
#         # copy model structure
#         dc_new = kwargs['dc'] if 'dc' in kwargs else mod_src.DCore
#         pc_new = kwargs['pc'] if 'pc' in kwargs else mod_src.DCore
#
#         mod_new = mod_src.clone(dc=dc_new, pc=pc_new)
#         mod_new.Obs.TimeSeries = mod_src.Obs.TimeSeries.copy()
#
#         return mod_new
#
#     def to_json(self):
#         js = dict()
#         js['Name'] = self.Name
#         js['Arguments'] = self.Arguments
#         js['Type'] = 'CoreODE'
#         js['TargetedPCore'] = self.TargetedPCore
#         js['TargetedDCore'] = self.TargetedDCore
#         js['Behaviours'] = self.Behaviours
#         js['Observation'] = {k: v for k, v in zip(['State', 'Transition', 'Behaviour'], self.Obs_s_t_b)}
#
#         return js
#
#     @staticmethod
#     def from_json(js):
#         bp = BlueprintCoreODE(js['Name'], js['TargetedPCore'], js['TargetedDCore'])
#         for k, v in js['Arguments']:
#             bp.set_arguments(k, v)
#         bp.Behaviours = deepcopy(js['Behaviours'])
#         obs = js['Observation']
#         bp.set_observations(obs['State'], obs['Transition'], obs['Behaviour'])
#         return bp
