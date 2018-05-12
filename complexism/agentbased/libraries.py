from complexism.agentbased.be import *
from epidag.factory import get_workshop
import epidag.factory.arguments as vld

__author__ = 'TimeWz667'
__all__ = []


# Behaviour library
BehaviourLibrary = get_workshop('ABM_BE')

BehaviourLibrary.register('Cohort', Cohort, [vld.Options('s_death', 'states')])
BehaviourLibrary.register('Reincarnation', Reincarnation,
                          [vld.Options('s_death', 'states'), vld.Options('s_birth', 'states')])
BehaviourLibrary.register('DemoDynamic', TimeSeriesLife,
                          [vld.Options('s_death', 'states'), vld.Options('s_birth', 'states'),
                           vld.Options('t_death', 'transitions'), vld.NotNull('demo')])
BehaviourLibrary.register('LifeRate', LifeRate,
                          [vld.Options('s_death', 'states'), vld.Options('s_birth', 'states'),
                           vld.PositiveFloat('rate'), vld.PositiveFloat('dt', opt=True, default=0.5)])
BehaviourLibrary.register('LifeS', LifeS,
                          [vld.Options('s_death', 'states'), vld.Options('s_birth', 'states'),
                           vld.PositiveFloat('rate'), vld.PositiveFloat('dt', opt=True, default=0.5),
                           vld.PositiveFloat('cap')])
BehaviourLibrary.register('LifeLeeCarter', LifeLeeCarter,
                          [vld.Options('s_death', 'states'), vld.Options('s_birth', 'states'),
                           vld.Options('t_death', 'transitions'), vld.PositiveInteger('yr'),
                           vld.Path('path_lct'), vld.Path('path_lcx'), vld.Path('path_nb'), vld.Path('path_agestr'),
                           vld.PositiveFloat('rmf', default=1.07)])


BehaviourLibrary.register('TimeStep', TimeStep,
                          [vld.Options('t_tar', 'transitions'), vld.List('ys'), vld.List('ts')])
BehaviourLibrary.register('ForeignShock', ForeignShock,
                          [vld.Options('t_tar', 'transitions'),
                           vld.String('mod_src', opt=True),
                           vld.String('par_src', opt=True)])

