from epidag import DirectedAcyclicGraph
import json
from dzdy.dcore import build_from_script, build_from_json, BlueprintCTBN, BlueprintCTMC
from dzdy.abmodel import BlueprintABM
from dzdy.ebmodel import BlueprintCoreODE
from dzdy.multimodel import ModelLayout
from dzdy.mcore import Simulator

__author__ = 'TimeWz667'


__all__ = ['load_txt', 'load_json', 'save_json',
           'read_pc', 'load_pc', 'save_pc',
           'read_dc', 'load_dc', 'save_dc', 'new_dc',
           'generate_pc', 'generate_dc', 'generate_pc_dc',
           'load_mc', 'save_mc', 'new_mc', 'generate_model', 'copy_model',
           'new_abm', 'generate_abm', 'copy_abm',
           'add_abm_behaviour', 'add_abm_fillup', 'add_abm_network', 'set_abm_observations',
           'new_core_ode', 'generate_core_ode', 'copy_core_ode',
           'add_core_ode_behaviour',
           'load_layout', 'save_layout', 'new_layout', 'add_layout_entry', 'generate_multimodel',
           'simulate', 'update']


def write_info_log(log, msg):
    log.info(msg)


def write_debug_log(log, msg):
    log.debug(msg)


def load_txt(path, log=None):
    """
    Load txt file given path
    Args:
        path (str): path of a txt file

    Returns:
        string of the txt file
    """
    with open(path, 'r') as f:
        return str(f.read())


def load_json(path, log=None):
    """
    Load json file given path
    Args:
        path (str): path of a json file

    Returns:
        json of the json file
    """
    with open(path, 'r') as f:
        return json.load(f)


def save_json(js, path, log=None):
    """
    Save a dictionary into a json file
    Args:
        js (dict):
        path (str):

    """
    with open(path, 'w') as f:
        json.dump(js, f)


def read_pc(script, log=None):
    """
    Read PC from script
    Args:
        script(str): script of pc

    Returns:
        a blueprint of parameter core
    """
    return DirectedAcyclicGraph(script).get_simulation_model()


def load_pc(js, log=None):
    """
    Turn pc into js
    Args:
        js(dict): json file as a dictionary

    Returns:
        a blueprint of parameter core
    """
    return DirectedAcyclicGraph.from_json(js).get_simulation_model()


def save_pc(pc, path, log=None):
    save_json(pc.to_json(), path)


def read_dc(script, log=None):
    return build_from_script(script)


def load_dc(js, log=None):
    return build_from_json(js)


def save_dc(dc, path, log=None):
    save_json(dc.to_json(), path)


def new_dc(name, dc_type, log=None):
    """
    Initialise a new blueprint of dynamic core
    Args:
        name(string): name of the DC
        dc_type(string): CTMC (continuous-time markov chain) or CTBN (continuous-time Bayesian network)

    Returns:
        a blueprint of dynamic core
    """
    if dc_type == 'CTMC':
        return BlueprintCTMC(name)
    elif dc_type == 'CTBN':
        return BlueprintCTBN(name)


def load_mc(js, log=None):
    """
    Load a blueprint of model
    Args:
        js(json): json file as a dictionary

    Returns:

    """
    if js['Type'] == 'ABM':
        return BlueprintABM.from_json(js)


def save_mc(dc, path, log=None):
    save_json(dc.to_json(), path)


def new_abm(name, tar_pc, tar_dc, log=None):
    bp_abm = BlueprintABM(name, tar_pc, tar_dc)
    return bp_abm


def new_core_ode(name, tar_pc, tar_dc, log=None):
    bp_ebm = BlueprintCoreODE(name, tar_pc, tar_dc)
    return bp_ebm

def new_fn_ode(name, tar_pc, log=None):
    pass

def new_mc(name, model_type, log=None, **kwargs):
    if model_type == 'ABM':
        return new_abm(name, kwargs['tar_pc'], kwargs['tar_dc'], log)
    elif model_type == 'CoreODE':
        return new_core_ode(name, kwargs['tar_pc'], kwargs['tar_dc'], log)
    elif model_type == 'FnODE':
        return new_fn_ode(name, kwargs['tar_pc'], log)
    else:
        raise ValueError('No this type of model')


def load_layout(js, log=None):
    return ModelLayout.from_json(js)


def save_layout(layout, path, log=None):
    save_json(layout.to_json(), path)


def new_layout(name, log=None):
    return ModelLayout(name)


def add_layout_entry(layout, model_name, y0, log=None, **kwargs):
    """
    Add a sub-model entry into layout
    Args:
        layout: target layout
        model_name: name of prefix of model(s)
        y0: inital values
        log(Logging): logging object, None if not logging
        **kwargs: iteration rule (size), (fr, size), (fr, to), (fr, to, by)

    Returns:

    """
    pass


def add_abm_fillup(bp_mc, fu_type, log=None, **kwargs):
    bp_mc.add_fillup(fu_type, **kwargs)


def add_abm_network(bp_mc, net_name, net_type, log=None, **kwargs):
    bp_mc.add_network(net_name, net_type, **kwargs)


def add_abm_behaviour(bp_mc, be_name, be_type, log=None, **kwargs):
    bp_mc.add_behaviour(be_name, be_type, **kwargs)


def set_abm_observations(bp_mc, states=None, transitions=None, behaviours=None, log=None):
    bp_mc.set_observations(states, transitions, behaviours)


def add_core_ode_behaviour(bp_mc, be_name, be_type, log=None, **kwargs):
    bp_mc.add_behaviour(be_name, be_type, **kwargs)


def set_core_ode_observations(bp_mc, states=None, transitions=None, behaviours=None, log=None):
    bp_mc.set_observations(states, transitions, behaviours)


def generate_pc(bp_pc, log=None):
    """
    generate a parameter core
    Args:
        bp_pc (SimulationModel): a blueprint of pc
        log (Logging): logging object

    Returns:
        parameter core
    """
    return bp_pc.sample_core()


def generate_dc(bp_dc, pc, log=None):
    """
    generate a dynamic core
    :param pc: parameter core
    :param bp_dc: blueprint of targeted dynamic core
    :return: dynamic core
    """
    if not bp_dc.is_compatible(pc):
        raise ValueError('Not compatible pcore')
    return bp_dc.generate_model(pc)


def generate_pc_dc(bp_pc, bp_dc, one_one=True, size=1, log=None):
    """
    generate set of pc and dc
    Args:
        bp_pc:
        bp_dc:
        one_one:
        size:
        log:

    Returns:

    """
    if one_one and size > 0:
        if size == 1:
            pc = generate_pc(bp_pc)
            return pc, generate_dc(bp_dc, pc)
        else:
            pd_list = list()
            for _ in range(size):
                pc = generate_pc(bp_pc)
                dc = generate_dc(bp_dc, pc)
                pd_list.append((pc, dc))
            return pd_list

    else:
        pc_proto = generate_pc(bp_pc)
        pd_list = list()
        for _ in range(size):
            pc = pc_proto.clone()
            dc = generate_dc(bp_dc, pc)
            pd_list.append((pc, dc))
        return pd_list


def generate_abm(bp_mc, pc=None, dc=None, name=None, log=None, **kwargs):
    """
    generate an agent-based model
    :param bp_mc: blueprint of ABM
    :param pc: parameter core
    :param dc: dynamic core
    :param name: name of new ABM
    :param log:
    :return: empty ABM
    """
    if not name:
        name = bp_mc.Name
    return bp_mc.generate(name, pc=pc, dc=dc, **kwargs)


def generate_core_ode(bp_mc, pc=None, dc=None, name=None, log=None, **kwargs):
    if not name:
        name = bp_mc.Name
    return bp_mc.generate(name, pc=pc, dc=dc, **kwargs)


def generate_multimodel(layout, pcs, dcs, mcs, log=None):
    pass


def generate_model(bp_mc, pc, dc, name=None, log=None, **kwargs):
    if isinstance(bp_mc, BlueprintABM):
        return generate_abm(bp_mc, pc, dc, name, **kwargs)
    elif isinstance(bp_mc, BlueprintCoreODE):
        return generate_core_ode(bp_mc, pc, dc, name, **kwargs)


def copy_abm(mod_src, bp_mc, bp_pc, bp_dc, tr_tte=True, pc_new=False, intervention=None, log=None):
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


def copy_core_ode(mod_src, bp_mc, bp_pc, bp_dc, pc_new=False, intervention=None, log=None):
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


def copy_model(mod_src, bp_mc, bp_pc, bp_dc, tr_tte=True, pc_new=False, intervention=None, log=None):
    """
    copy a simulation model
    :param mod_src: model to be replicated
    :param bp_mc: blueprint of source model
    :param bp_pc: blueprint of targeted parameter core
    :param bp_dc: blueprint of targeted dynamic model
    :param pc_new: True if new parameter core required
    :param tr_tte: keep not intervened time to event or not
    :param intervention: dictionary for variables to be intervened
    :return: a copied ABM
    """
    if isinstance(bp_mc, BlueprintABM):
        return copy_abm(mod_src, bp_mc, bp_pc, bp_dc, tr_tte, pc_new, intervention)
    elif isinstance(bp_mc, BlueprintCoreODE):
        return copy_core_ode(mod_src, bp_mc, bp_pc, bp_dc, pc_new, intervention)


def copy_multimodel(mm_src, layout, bp_mcs, bp_pcs, bp_dcs, log=None):
    pass


def simulate(model, y0, fr, to, dt=1, log=None):
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
        if log:
            write_debug_log(log, 'Please use update instead of simulation')
        return model.output()
    sim = Simulator(model)
    sim.simulate(y0, fr, to, dt)
    return model.output()


def update(model, to, dt=1, log=None):
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
