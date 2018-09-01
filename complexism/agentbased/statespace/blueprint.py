import epidag as dag
from epidag.factory import get_workshop
import complexism as cx
from complexism.mcore import AbsBlueprintMCore
from .abmstsp import StSpAgentBasedModel, StSpY0
from .breeder import StSpBreeder

__author__ = 'TimeWz667'
__all__ = ['BlueprintStSpABM']


class BlueprintStSpABM(AbsBlueprintMCore):
    def __init__(self, name):
        AbsBlueprintMCore.__init__(self, name)
        self.Population = {'Agent': {}, 'Networks': []}
        self.Behaviours = list()
        self.ObsBehaviours = list()
        self.ObsStates = list()
        self.ObsTransitions = list()
        self.ObsFunctions = list()

    def set_agent(self, dynamics, prefix='Ag', group=None, exo=None, **kwargs):
        self.Population['Agent'] = {
            'Prefix': prefix,
            'Group': group if group else 'agent',
            'Type': 'stsp',
            'Exo': dict(exo) if exo else dict(),
            'Dynamics': dynamics if dynamics else None,
            'Args': dict(kwargs)
        }

    def add_network(self, net_name, net_type, **kwargs):
        self.Population['Networks'].append({
            'Name': net_name,
            'Type': net_type,
            'Args': dict(kwargs)
        })

    def add_network_json(self, js):
        self.Population['Networks'].append(js)

    def add_behaviour(self, be_name, be_type, **kwargs):
        self.Behaviours.append({"Name": be_name, 'Type': be_type, 'Args': dict(kwargs)})

    def set_observations(self, states=None, transitions=None, behaviours=None, functions=None):
        if states:
            self.ObsStates = list(states)
        if transitions:
            self.ObsTransitions = list(transitions)
        if behaviours:
            self.ObsBehaviours = list(behaviours)
        if functions:
            self.ObsFunctions = list(functions)

    def get_parameter_hierarchy(self, da=None, dc=None):
        if dc:
            if isinstance(dc, str):
                dc = da.get_state_space_model(dc)
            elif not isinstance(dc, cx.AbsBlueprint):
                raise KeyError('Unknown state space model')
        elif da:
            dc = da.get_state_space_model(self.Population['Agent']['Dynamics'])

        ag_gp = self.Population['Agent']['Group']
        trs = dc.RequiredSamplers
        return {
            self.Name: [ag_gp],
            ag_gp: trs
        }

    def get_y0_proto(self):
        return StSpY0()

    def generate(self, name, **kwargs):
        # Prepare PC, DC

        da = kwargs['da'] if 'da' in kwargs else None

        pc = kwargs['pc'] if 'pc' in kwargs else None
        bn = kwargs['bn'] if 'bn' in kwargs else None

        if pc is not None:
            if isinstance(pc, str):
                bn, pc = pc, None
        elif not bn:
            raise KeyError('Missing parameter-related information')

        if pc is None:
            if isinstance(bn, str):
                try:
                    bn = da.get_bayes_net(bn)
                except KeyError as e:
                    raise e

            elif not isinstance(bn, dag.BayesianNetwork):
                raise TypeError('Unknown type parameters')

        ss = kwargs['ss'] if 'ss' in kwargs else self.Population['Agent']['Dynamics']
        if isinstance(ss, str) and da:
            try:
                ss = da.get_state_space_model(ss)
            except KeyError as e:
                raise e
        elif not isinstance(ss, cx.AbsBlueprint):
            raise TypeError('da(Direct) required for identifying state-space')

        if pc is None:
            hie = self.get_parameter_hierarchy(dc=ss)
            sm = dag.as_simulation_core(bn, hie=hie)
            pc = sm.generate(name, exo=kwargs['exo'] if 'exo' in kwargs else None)

        ss = ss.generate_model(name, **pc.get_prototype(group=self.Population['Agent']['Group']).get_samplers())

        # Generate population
        ag = self.Population['Agent']
        eve = StSpBreeder(ag['Prefix'], ag['Group'], pc, ss)
        pop = cx.Population(eve)
        model = StSpAgentBasedModel(name, pc, pop)

        # Set resources
        resources = {
            'states': model.DCore.States,
            'transitions': model.DCore.Transitions,
            'networks': [net['Name'] for net in self.Population['Networks']]
        }
        resources.update(pc.Locus)

        # Install networks
        ws = get_workshop('Networks')
        ws.renew_resources(resources)
        for net in self.Population['Networks']:
            net = ws.create(net)
            model.add_network(net)
        ws.clear_resources()

        # Install behaviours
        ws = get_workshop('StSpABM_BE')
        ws.renew_resources(resources)
        for be in self.Behaviours:
            be = ws.create(be)
            model.add_behaviour(be)
        ws.clear_resources()

        # Assign observations
        for st in self.ObsStates:
            model.add_observing_state(st)

        for tr in self.ObsTransitions:
            model.add_observing_transition(tr)

        for be in self.ObsBehaviours:
            model.add_observing_behaviour(be)

        for func in self.ObsFunctions:
            model.add_observing_function(func)

        return model

    def to_json(self):
        # todo
        pass

    def clone(self, mod_src, **kwargs):
        # todo
        pass

    @staticmethod
    def from_json(js):
        # todo
        pass
