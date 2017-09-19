from dzdy.abmodel.be import *
import os

__author__ = 'TimeWz667'


BehaviourLibrary = dict()


def register_behaviour(name, args):
    BehaviourLibrary[name] = {'Type': eval(name), 'Args': args}


def check_arguments(mod, be_type, kwargs):
    dc = mod.DCore
    args = BehaviourLibrary[be_type]['Args']
    for arg in args:
        try:
            v = kwargs[arg]
        except KeyError:
            print('Argument {} lost'.format(arg))
            return False
        else:
            if arg.startswith('s_'):
                if v not in dc.States:
                    print('State {} does not exist'.format(arg))
                    return False
            elif arg.startswith('t_'):
                if v not in dc.Transitions:
                    print('Transitions {} does not exist'.format(arg))
                    return False
            elif arg.startswith('path_'):
                if not os.path.isfile(v):
                    print('File {} does not exist'.format(arg))
                    return False
    return True


def install_behaviour(mod, be_name, be_type, kwargs):
    if check_arguments(mod, be_type, kwargs):
        BehaviourLibrary[be_type]['Type'].decorate(be_name, mod, **kwargs)


register_behaviour('Reincarnation', ['s_birth', 's_death'])
register_behaviour('Cohort', ['s_death'])
register_behaviour('LifeRate', ['s_birth', 's_death', 'rate', 'dt'])
register_behaviour('LifeS', ['s_birth', 's_death', 'cap', 'rate', 'dt'])
register_behaviour('LifeLeeCarter', ['s_birth', 's_death', 't_death', 'yr',
                                     'path_lct', 'path_lcx', 'path_nb', 'path_agestr', 'rmf'])

register_behaviour('ComFDShock', ['s_src', 't_tar'])
register_behaviour('ComFDShockFast', ['s_src', 't_tar', 'dt'])
register_behaviour('ComDDShock', ['s_src', 't_tar'])
register_behaviour('ComDDShockFast', ['s_src', 't_tar', 'dt'])
register_behaviour('ComWeightSumShock', ['s_src', 't_tar', 'weight', 'dt'])
register_behaviour('ComWeightAvgShock', ['s_src', 't_tar', 'weight', 'dt'])
register_behaviour('NetShock', ['s_src', 't_tar', 'net'])
register_behaviour('NetWeightShock', ['s_src', 't_tar', 'net', 'weight'])
register_behaviour('NerfDecision', ['s_src', 't_tar', 'prob'])
register_behaviour('BuffDecision', ['s_src', 't_tar', 'prob'])

register_behaviour('TimeVaryingInterp', ['t_tar', 'ts', 'y', 'dt'])
register_behaviour('TimeVarying', ['t_tar', 'func', 'dt'])
register_behaviour('TimeStep', ['t_tar', 'ys', 'ts'])

register_behaviour('ForeignShock', ['t_tar'])
register_behaviour('ForeignAddShock', ['t_tar'])



# effect with table
# effect with regression
# APC model
