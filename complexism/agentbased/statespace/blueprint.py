import epidag as dag
from epidag.factory import get_workshop
import complexism as cx
from complexism.mcore import AbsBlueprintMCore
from .abmstsp import StSpAgentBasedModel
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

    def set_agent(self, prefix='Ag', group=None, exo=None, dynamics=None, **kwargs):
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

    def get_parameter_hierarchy(self, **kwargs):
        dc = kwargs['dc']
        ag_gp = self.Population['Agent']['Group']
        trs = dc.RequiredSamplers
        return {
            self.Name: [ag_gp],
            ag_gp: trs
        }

    def generate(self, name, **kwargs):
        # Prepare PC, DC
        dc = kwargs['dc']

        if 'pc' in kwargs:
            pc = kwargs['pc']
        elif 'sm' in kwargs:
            sm = kwargs['sm']
            pc = sm.generate(name, exo=kwargs['exo'] if 'exo' in kwargs else None)
        elif 'bn' in kwargs:
            bn = kwargs['bn']
            random = kwargs['random'] if 'random' in kwargs else []
            hie = kwargs['hie'] if 'hie' in kwargs else self.get_parameter_hierarchy(dc=dc)
            sm = dag.as_simulation_core(bn, hie=hie, random=random)
            pc = sm.generate(name, exo=kwargs['exo'] if 'exo' in kwargs else None)
        else:
            raise KeyError('Parameter core not found')

        # Generate population
        ag = self.Population['Agent']
        eve = StSpBreeder(ag['Prefix'], ag['Group'], pc, dc)
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
