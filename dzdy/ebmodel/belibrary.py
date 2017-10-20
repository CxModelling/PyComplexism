from dzdy.ebmodel.behaviour import *
import logging
from factory.manager import ResourceManager
import factory.arguments as vld

__author__ = 'TimeWz667'

__all__ = ['register_behaviour', 'validate_behaviour',
           'get_behaviour', 'get_behaviour_from_json',
           'get_behaviour_template', 'get_behaviour_defaults',
           'install_behaviour_from_json', 'install_behaviour', 'BehaviourLibrary']

logger = logging.getLogger(__name__)

# Network library
EBMBehaviourLibrary = ResourceManager()

EBMBehaviourLibrary.register('Multiplier', Multiplier, [vld.Options('t_tar', 'transitions')])

EBMBehaviourLibrary.register('InfectionFD', InfectionFD,
                             [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states')])

EBMBehaviourLibrary.register('InfectionDD', InfectionDD,
                             [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states')])

EBMBehaviourLibrary.register('Cohort', Cohort, [vld.Options('s_death', 'states')])

EBMBehaviourLibrary.register('Reincarnation', Reincarnation,
                             [vld.Options('s_death', 'states'), vld.Options('s_birth', 'states')])

EBMBehaviourLibrary.register('DemoDynamic', DemoDynamic,
                             [vld.Options('s_death', 'states'), vld.Options('s_birth', 'states'),
                              vld.Options('t_death', 'transitions'), vld.NotNull('demo')])

EBMBehaviourLibrary.register('TimeStep', TimeStep,
                             [vld.Options('t_tar', 'transitions'),
                              vld.ListString('ys'), vld.ListString('ts')])


def get_ebm_behaviour_from_json(js):
    return EBMBehaviourLibrary.create(js, logger=logger)


def get_ebm_behaviour(be_name, be_type, kwargs):
    js = {'Name': be_name, 'Type': be_type, 'Args': kwargs}
    return get_ebm_behaviour_from_json(js)


def get_ebm_behaviour_template(be_type):
    return EBMBehaviourLibrary.get_form(be_type)


def install_ebm_behaviour(mod, be_name, be_type, kwargs):
    be = get_ebm_behaviour(be_name, be_type, kwargs)
    mod.ODE.add_behaviour(be)


def install_ebm_behaviour_from_json(mod, js):
    be = get_ebm_behaviour_from_json(js)
    mod.ODE.add_behaviour(be)


def list_ebm_behaviours():
    return EBMBehaviourLibrary.list()
