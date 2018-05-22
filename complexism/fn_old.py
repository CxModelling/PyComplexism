import epidag as dag
from complexism.misc import *
from .dcore.fn import *
from .dcore import BlueprintCTMC, BlueprintCTBN
from complexism.agentbased.statespace import BlueprintStSpABM
# from complexism.ebmodel import BlueprintCoreODE
from complexism.multimodel import ModelLayout
from complexism.mcore import Simulator

__author__ = 'TimeWz667'


__all__ = ['load_txt', 'load_json',
           'read_pc', 'load_pc', 'save_pc',
           'read_dc', 'load_dc', 'save_dc', 'new_dc',
           'generate_pc', 'generate_dc', 'generate_pc_dc',
           'load_mc', 'save_mc', 'new_mc', 'generate_model', 'copy_model',
           'new_ssabm', 'generate_abm', 'copy_abm',
           'add_abm_behaviour', 'add_abm_network', 'set_abm_observations',
           'new_core_ode', 'generate_core_ode', 'copy_core_ode',
           'add_core_ode_behaviour',
           'load_layout', 'save_layout', 'new_layout', 'add_layout_entry', 'generate_multimodel',
           'simulate', 'update']



def load_mc(js):
    """
    Load a MC from json format
    :param js: model core in json
    :return: a blueprint of model core
    """
    if js['Type'] == 'SSABM':
        return BlueprintStSpABM.from_json(js)
    # elif js['Type'] == 'CoreODE':
    #     return BlueprintCoreODE.from_json(js)


def save_mc(mc, path):
    """
    Output a mc to file system
    :param mc: model core
    :param path: file path
    """
    save_json(mc.to_json(), path)


def new_ssabm(name):
    """
    Generate a new State-space ABM blueprint
    :param name: name
    :return: ABM blueprint
    """
    bp_abm = BlueprintStSpABM(name)
    return bp_abm


def new_core_ode(name, tar_pc, tar_dc):
    """
    Generate a new ODE blueprint (ODE with dynamic core)
    :param name: name of blueprint
    :param tar_pc: name of targeted pc
    :param tar_dc: name of targeted dc
    :return: ODE blueprint
    """
    bp_ebm = BlueprintCoreODE(name, tar_pc, tar_dc)
    return bp_ebm


def new_fn_ode(name, tar_pc):
    # todo
    pass


def new_mc(name, model_type, **kwargs):
    """
    Generate a new model blueprint
    :param name: name of model blueprint
    :param model_type: ABM, CoreODE, or FnODE
    :param kwargs: tar_pc, tar_dc, ... if applicable
    :return: model blueprint
    """
    if model_type == 'SSABM':
        return new_ssabm(name)
    elif model_type == 'CoreODE':
        return new_core_ode(name, kwargs['tar_pc'], kwargs['tar_dc'])
    elif model_type == 'FnODE':
        return new_fn_ode(name, kwargs['tar_pc'])
    else:
        raise ValueError('No this type of model')


def load_layout(js):
    """
    Load model layout from json format
    :param js: json
    :return: model layout
    """
    return ModelLayout.from_json(js)


def save_layout(layout, path):
    """
    Output model layout to file system
    :param layout: model layout
    :param path: file path
    """
    save_json(layout.to_json(), path)


def new_layout(name):
    """
    Generate a new blueprint of layout
    :param name: name of blueprint
    :return: blueprint of layout
    """
    return ModelLayout(name)


def add_layout_entry(layout, model_name, y0, **kwargs):
    """
    Add a sub-model entry into layout
    :param layout: model layout
    :param model_name: prefix of model(s)
    :param y0: initial values
    :param kwargs: iteration rule (size), (fr, size), (fr, to), (fr, to, by)
    :return:
    """
    # todo
    pass


def add_abm_network(bp_mc, net_name, net_type, **kwargs):
    bp_mc.add_network(net_name, net_type, **kwargs)


def add_abm_behaviour(bp_mc, be_name, be_type, **kwargs):
    bp_mc.add_behaviour(be_name, be_type, **kwargs)


def set_abm_observations(bp_mc, states=None, transitions=None, behaviours=None):
    bp_mc.set_observations(states, transitions, behaviours)


def add_core_ode_behaviour(bp_mc, be_name, be_type, **kwargs):
    bp_mc.add_behaviour(be_name, be_type, **kwargs)


def set_core_ode_observations(bp_mc, states=None, transitions=None, behaviours=None):
    bp_mc.set_observations(states, transitions, behaviours)


def generate_pc(bp_pc, cond=None):
    """
    Generate a parameter core
    :param cond: condition of parameters
    :param bp_pc: a blueprint of pc
    :return:
    """
    if cond:
        return bp_pc.sample_core(cond)
    else:
        return bp_pc.sample_core()


def generate_dc(bp_dc, pc):
    """
    generate a dynamic core
    :param pc: parameter core
    :param bp_dc: blueprint of targeted dynamic core
    :return: dynamic core
    """
    if not bp_dc.is_compatible(pc):
        raise ValueError('Not compatible pcore')
    return bp_dc.generate_model(pc)


def generate_pc_dc(bp_pc, bp_dc, cond=None, one_one=True, size=1):
    """

    :param bp_pc:
    :param bp_dc:
    :param cond:
    :param one_one:
    :param size:
    :return:
    """
    if one_one and size > 0:
        if size == 1:
            pc = generate_pc(bp_pc, cond)
            return pc, generate_dc(bp_dc, pc)
        else:
            pd_list = list()
            for _ in range(size):
                pc = generate_pc(bp_pc, cond)
                dc = generate_dc(bp_dc, pc)
                pd_list.append((pc, dc))
            return pd_list

    else:
        pc_proto = generate_pc(bp_pc, cond)
        pd_list = list()
        for _ in range(size):
            pc = pc_proto.clone()
            dc = generate_dc(bp_dc, pc)
            pd_list.append((pc, dc))
        return pd_list


def generate_abm(bp_mc, pc=None, dc=None, name=None, **kwargs):
    """
    Generate an agent-based model
    :param bp_mc: blueprint of ABM
    :param pc: parameter core
    :param dc: dynamic core
    :param name: name of new ABM
    :return: empty ABM
    """
    if not name:
        name = bp_mc.Name
    return bp_mc.generate(name, pc=pc, dc=dc, **kwargs)


def generate_core_ode(bp_mc, pc=None, dc=None, name=None, **kwargs):
    if not name:
        name = bp_mc.Name
    return bp_mc.generate(name, pc=pc, dc=dc, **kwargs)


def generate_multimodel(layout, pcs, dcs, mcs):
    # todo
    pass


def generate_model(bp_mc, pc, dc, name=None, **kwargs):
    if isinstance(bp_mc, BlueprintABM):
        return generate_abm(bp_mc, pc, dc, name, **kwargs)
    elif isinstance(bp_mc, BlueprintCoreODE):
        return generate_core_ode(bp_mc, pc, dc, name, **kwargs)


def copy_abm(mod_src, bp_mc, bp_pc, bp_dc, tr_tte=True, pc_new=False, intervention=None):
    """
    Copy an agent-based model
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


def copy_core_ode(mod_src, bp_mc, bp_pc, bp_dc, pc_new=False, intervention=None):
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
    :param tr_tte: keep not intervened time to event or not
    :param intervention: dictionary for variables to be intervened
    :return: a copied ABM
    """
    if isinstance(bp_mc, BlueprintABM):
        return copy_abm(mod_src, bp_mc, bp_pc, bp_dc, tr_tte, pc_new, intervention)
    elif isinstance(bp_mc, BlueprintCoreODE):
        return copy_core_ode(mod_src, bp_mc, bp_pc, bp_dc, pc_new, intervention)


def copy_multimodel(mm_src, layout, bp_mcs, bp_pcs, bp_dcs, log=None):
    # todo
    pass