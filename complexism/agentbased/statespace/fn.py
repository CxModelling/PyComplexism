import epidag as dag
from epidag.factory import get_workshop
from .. import Population
from .breeder import StSpBreeder
from .abmstsp import StSpAgentBasedModel

__author__ = 'TimeWz667'
__all__ = ['prepare_pc', 'generate_plain_model',
           'install_behaviour', 'install_network',
           'set_observations']


def form_resources(model):
    pc, dc = model.Parameters, model.DCore
    resources = {
        'states': dc.States,
        'transitions': dc.Transitions,
        'networks': model.Population.Networks.list()
    }
    resources.update(pc.Locus)
    return resources


def prepare_pc(model_name, ag_group, dbp, **kwargs):
    if 'pc' in kwargs:
        pc = kwargs['pc']
    elif 'sm' in kwargs:
        sm = kwargs['sm']
        pc = sm.generate(model_name, exo=kwargs['exo'] if 'exo' in kwargs else None)
    elif 'bn' in kwargs:
        bn = kwargs['bn']
        random = kwargs['random'] if 'random' in kwargs else []
        if 'hie' in kwargs:
            hie = kwargs['hie']
        else:
            trs = dbp.RequiredSamplers
            hie = {
                model_name: [ag_group],
                ag_group: trs
            }
        sm = dag.as_simulation_core(bn, hie=hie, random=random)
        pc = sm.generate(model_name, exo=kwargs['exo'] if 'exo' in kwargs else None)
    else:
        raise KeyError('Parameter core not found')
    return pc


def generate_plain_model(model_name, dbp, pc, prefix='Ag', group=None, have_network=False):
    group = group if group else prefix
    eve = StSpBreeder(prefix, group, pc, dbp)
    pop = Population(eve)
    return StSpAgentBasedModel(model_name, pc, pop)


def install_network(model, net_name, net_type, resources=None, **kwargs):
    res = resources if resources else form_resources(model)
    js = {'Name': net_name, 'Type': net_type, 'Args': dict(kwargs)}
    ws = get_workshop('Networks')
    ws.renew_resources(res)

    net = ws.create(js)
    model.add_network(net)

    ws.clear_resources()


def install_behaviour(model, be_name, be_type, resources=None, **kwargs):
    res = resources if resources else form_resources(model)
    js = {'Name': be_name, 'Type': be_type, 'Args': dict(kwargs)}
    ws = get_workshop('StSpABM_BE')
    ws.renew_resources(res)

    be = ws.create_from_json(js)
    model.Behaviours[be.Name] = be

    ws.clear_resources()


def set_observations(model, states=list(), transitions=list(), behaviours=list(), functions=list()):
    # Assign observations
    for st in states:
        model.add_observing_state(st)

    for tr in transitions:
        model.add_observing_transition(tr)

    for be in behaviours:
        model.add_observing_behaviour(be)

    for func in functions:
        model.add_observing_function(func)




