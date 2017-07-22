from epidag import DirectedAcyclicGraph
import json
from dzdy.dcore import build_from_script, build_from_json, BlueprintCTBN, BlueprintCTMC
from dzdy.abmodel import BlueprintABM
from dzdy.multimodel import ModelLayout
from dzdy.mcore import Simulator

__author__ = 'TimeWz667'


def load_txt(path):
    with open(path, 'r') as f:
        return str(f.read())


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_json(js, path):
    with open(path, 'w') as f:
        json.dump(js, f)


def read_pc(script):
    return DirectedAcyclicGraph(script).get_simulation_model()


def load_pc(js):
    return DirectedAcyclicGraph.from_json(js).get_simulation_model()


def save_pc(pc, path):
    save_json(pc.to_json(), path)


def read_dc(script):
    return build_from_script(script)


def load_dc(js):
    return build_from_json(js)


def save_dc(dc, path):
    save_json(dc.to_json(), path)


def new_dc(name, dc_type):
    if dc_type == 'CTMC':
        return BlueprintCTMC(name)
    elif dc_type == 'CTBN':
        return BlueprintCTBN(name)


def load_mc(js):
    if js['Type'] == 'ABM':
        return BlueprintABM.from_json(js)


def save_mc(dc, path):
    save_json(dc.to_json(), path)


def new_abm(name, tar_pc, tar_dc):
    bp_abm = BlueprintABM(name, tar_pc, tar_dc)
    return bp_abm


def new_ebm(name, tar_pc, tar_dc):
    pass


def new_mc(name, model_type, **kwargs):
    if model_type == 'ABM':
        return new_abm(name, kwargs['tar_pc'], kwargs['tar_dc'])
    elif model_type == 'EBM':
        return new_ebm(name, kwargs['tar_pc'], kwargs['tar_dc'])
    else:
        raise ValueError('No this type of model')


def load_layout(js):
    return ModelLayout.from_json(js)


def save_layout(layout, path):
    save_json(layout.to_json(), path)


def new_layout(name):
    return ModelLayout(name)


def add_abm_fillup(bp_mc, fu_type, **kwargs):
    bp_mc.add_fillup(fu_type, **kwargs)


def add_abm_network(bp_mc, net_name, net_type, **kwargs):
    bp_mc.add_network(net_name, net_type, **kwargs)


def add_abm_behaviour(bp_mc, be_name, be_type, **kwargs):
    bp_mc.add_behaviour(be_name, be_type, **kwargs)


def set_abm_observations(bp_mc, states=None, transitions=None, behaviours=None):
    bp_mc.set_observations(states, transitions, behaviours)


def generate_pc(bp_pc):
    """
    generate a parameter core
    :param bp_pc: parameter core
    :param new_name: nickname for new dynamic core
    :return: parameter core
    """
    return bp_pc.sample_core()


def generate_dc(bp_dc, pc, new_name=None):
    """
    generate a dynamic core
    :param pc: parameter core
    :param bp_dc: blueprint of targeted dynamic core
    :param new_name: nickname for new dynamic core
    :return: dynamic core
    """
    if not bp_dc.is_compatible(pc):
        raise ValueError('Not compatible pcore')
    return bp_dc.generate_model(pc, new_name)


def generate_abm(bp_mc, pc=None, dc=None, name=None, **kwargs):
    """
    generate an agent-based model
    :param bp_mc: blueprint of ABM
    :param pc: parameter core
    :param dc: dynamic core
    :param name: name of new ABM
    :return: empty ABM
    """
    if not name:
        name = bp_mc.Name
    return bp_mc.generate(name, pc=pc, dc=dc, **kwargs)


def generate_ebm(bp_mc, pc=None, dc=None, name=None, **kwargs):
    # todo
    pass


def generate_model(bp_mc, pc, dc, name=None, **kwargs):
    if isinstance(bp_mc, BlueprintABM):
        return generate_abm(bp_mc, pc, dc, name, **kwargs)
    else:
        return generate_ebm(bp_mc, pc, dc, name, **kwargs)


def copy_abm(mod_src, bp_mc, bp_pc, bp_dc, tr_tte=True, pc_new=False, intervention=None):
    """
    copy an agent-based model
    :param mod_src: model to be replicated
    :param bp_mc: blueprint of source model
    :param bp_pc: blueprint of targeted parameter core
    :param bp_dc: blueprint of targeted dynamic model
    :param tr_tte: True if tte values need to be copy
    :param pc_new: True if new parameter core required
    :param intervention: dictionary for variables to be intervened
    :return: a copied ABM
    """
    if pc_new:
        pc_new = bp_pc.sample_core()
    else:
        pc_new = mod_src.PCore.clone()

    if intervention:
        pc_new = bp_pc.intervene_core(pc_new, intervention)

    dc_new = bp_dc.generate_model(pc_new, mod_src.DCore.Name)
    return bp_mc.clone(mod_src, pc=pc_new, dc=dc_new, tr_tte=tr_tte)


def copy_ebm(mod_src, bp_mc, bp_pc, bp_dc, pc_new=False, intervention=None):
    """
    copy an equation-based model
    :param mod_src: model to be replicated
    :param bp_mc: blueprint of source model
    :param bp_pc: blueprint of targeted parameter core
    :param bp_dc: blueprint of targeted dynamic model
    :param pc_new: True if new parameter core required
    :param intervention: dictionary for variables to be intervened
    :return: a copied ABM
    """
    if pc_new:
        pc_new = bp_pc.sample_core()
    else:
        pc_new = mod_src.PCore.clone()

    if intervention:
        pc_new = bp_pc.intervene_core(pc_new, intervention)

    dc_new = bp_dc.generate_model(pc_new, mod_src.DCore.Name)
    return bp_mc.clone(mod_src, pc=pc_new, dc=dc_new)


def copy_model(mod_src, bp_mc, bp_pc, bp_dc, tr_tte=True, pc_new=False, intervention=None):
    """
    copy a simulation model
    :param mod_src: model to be replicated
    :param bp_mc: blueprint of source model
    :param bp_pc: blueprint of targeted parameter core
    :param bp_dc: blueprint of targeted dynamic model
    :param pc_new: True if new parameter core required
    :param intervention: dictionary for variables to be intervened
    :return: a copied ABM
    """
    if isinstance(bp_mc, BlueprintABM):
        return copy_abm(mod_src, bp_mc, bp_pc, bp_dc, tr_tte, pc_new, intervention)
    else:
        return copy_ebm(mod_src, bp_mc, bp_pc, bp_dc, pc_new, intervention)


def simulate(model, y0, fr, to, dt=1):
    """
    Simulate a dynamic model with initial values (y0)
    :param model: dynamic model
    :param y0: initial value
    :param fr: initial time point
    :param to: end time
    :param dt: observation interval
    :return: data of simulation
    """
    if model.TimeEnd:
        print('Please use update instead of simulation')
        return model.output()
    sim = Simulator(model)
    sim.simulate(y0, fr, to, dt)
    return model.output()


def update(model, to, dt=1):
    """
    Update a dynamic to a certain time point
    :param model: dynamic model which has been initialised
    :param to: end time
    :param dt: observation interval
    :return: data of simulation
    """
    sim = Simulator(model)
    sim.Time = model.TimeEnd
    if to > sim.Time:
        sim.update(to, dt)
    return model.output()
