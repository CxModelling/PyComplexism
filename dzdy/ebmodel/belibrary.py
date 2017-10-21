from dzdy.ebmodel.eqbehaviour import *
import logging
from factory import getWorkshop
import factory.arguments as vld

__author__ = 'TimeWz667'
__all__ = []

logger = logging.getLogger(__name__)


# Behaviour library
EBMBehaviourLibrary = getWorkshop('EBM_BE')

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
