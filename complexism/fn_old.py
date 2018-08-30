
__author__ = 'TimeWz667'


__all__ = ['copy_model',
'copy_abm',
'generate_core_ode', 'copy_core_ode',
]



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

