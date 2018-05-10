from .eqbehaviour import *
import logging
from epidag.factory import get_workshop
import epidag.factory.arguments as vld

__author__ = 'TimeWz667'
__all__ = []

logger = logging.getLogger(__name__)


# Behaviour library
EBMBehaviourLibrary = get_workshop('EBM_BE')

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
                             [vld.Options('t_tar', 'transitions'), vld.List('ys'), vld.List('ts')])


logger.info('EBM Behaviour library (EBM_BE) loaded')


def register_ebm_behaviour(name, cls, args):
    if not isinstance(name, str):
        raise TypeError('A behaviour name must be str')
    if not isinstance(name, Behaviour):
        raise TypeError('cls is not behaviour class for EBM')
    for arg in args:
        if not isinstance(arg, vld.Argument):
            raise TypeError('arg is not a well-defined argument')
    EBMBehaviourLibrary.register(name, cls, args)
