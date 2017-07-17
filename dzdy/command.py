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


def read_pcore(script):
    return DirectedAcyclicGraph(script).get_simulation_model()


def load_pcore(js):
    return DirectedAcyclicGraph.from_json(js).get_simulation_model()


def save_pcore(pc, path):
    save_json(pc.to_json(), path)


def read_dcore(script):
    return build_from_script(script)


def load_dcore(js):
    return build_from_json(js)


def save_dcore(dc, path):
    save_json(dc.to_json(), path)


def new_dcore(name, dc_type):
    if dc_type == 'CTMC':
        return BlueprintCTMC(name)
    elif dc_type == 'CTBN':
        return BlueprintCTBN(name)


def load_mcore(js):
    if js['Type'] == 'ABM':
        return BlueprintABM.from_json(js)


def save_mcore(dc, path):
    save_json(dc.to_json(), path)


def new_abm(name, tar_pcore, tar_dcore):
    bp_abm = BlueprintABM(name, tar_pcore, tar_dcore)
    return bp_abm


def new_mcore(name, model_type, **kwargs):
    if model_type == 'ABM':
        return new_abm(name, kwargs['tar_pcore'], kwargs['tar_dcore'])
    elif model_type == 'EBM':
        pass


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


def generate_pc_dc(bp_pc, bp_dc, new_name=None):
    """
    generate a pair of parameter core and dynamic core
    :param bp_pc: blueprint of targeted parameter core
    :param bp_dc: blueprint of targeted dynamic core
    :param new_name: nickname for new dynamic core
    :return: tuple, parameter core and dynamic core
    """
    pc = bp_pc.sample_core()
    if not bp_dc.is_compatible(pc):
        raise ValueError('Not compatible pcore')
    return pc, bp_dc.generate_model(pc, new_name)


def generate_abm(bp_mc, pc, dc, name=None):
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
    return bp_mc.generate(name, pc, dc)


def copy_abm(mod_src, mc_bp, pc_bp, dc_bp, tr_tte=True, pc_new=False, intervention=None):
    """
    copy an agent-based model
    :param mod_src: model to be replicated
    :param mc_bp: blueprint of source model
    :param pc_bp: blueprint of targeted parameter core
    :param dc_bp: blueprint of targeted dynamic model
    :param tr_tte: True if tte values need to be copy
    :param pc_new: True if new parameter core required
    :param intervention: dictionary for variables to be intervened
    :return: a copied ABM
    """
    if pc_new:
        pc_new = pc_bp.sample_core()
    else:
        pc_new = mod_src.PCore.clone()

    if intervention:
        pc_new = pc_bp.intervention_core(pc_new, intervention)

    dc_new = dc_bp.generate_model(pc_new, mod_src.DCore.Name)
    return mc_bp.clone(mod_src, pc_new, dc_new, tr_tte)


def generate_ebm_from_function():
    # todo
    pass


def generate_ebm_from_dcore():
    # todo a blueprint of ebm
    pass


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
