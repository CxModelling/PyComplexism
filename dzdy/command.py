from epidag import SimulationModel, DirectedAcyclicGraph
import json
import dcore
from abmodel import BlueprintABM

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
    return SimulationModel.from_json(js)


def save_pcore(pc, path):
    return save_json(pc.to_json(), path)


def read_dcore(script):
    return dcore.build_from_script(script)


def load_dcore(js):
    return dcore.build_from_json(js)


def save_dcore(dc, path):
    return save_json(dc.to_json(), path)


def new_dcore(name, dc_type):
    if dc_type == 'CTMC':
        return dcore.BlueprintCTMC(name)
    elif dc_type == 'CTBN':
        return dcore.BlueprintCTBN(name)


def load_mcore(js):
    if js['Type'] == 'ABM':
        return BlueprintABM.build_from_json(js)


def save_mcore(dc, path):
    return save_json(dc.to_json(), path)


def new_abm(name, tar_pcore, tar_dcore):
    bp_abm = BlueprintABM(name, tar_pcore, tar_dcore)
    return bp_abm


def new_mcore(name, model_type, **kwargs):
    if model_type == 'ABM':
        return new_abm(name, kwargs['tar_pcore'], kwargs['tar_dcore'])
    elif model_type == 'EBM':
        pass


def load_layout(js):
    # todo
    pass


def save_layout(layout, path):
    # todo
    pass


def new_layout(name):
    # todo
    pass


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
    elif intervention:
        pc_new = pc_bp.intervention_core(mod_src.PCore, intervention)
    else:
        pc_new = mod_src.PCore.clone()
    dc_new = dc_bp.generate_model(pc_new, mod_src.DCore.Name)
    return mc_bp.clone(mod_src, pc_new, dc_new, tr_tte)


def generate_ebm_from_function():
    pass


def generate_ebm_from_dcore():
    pass
