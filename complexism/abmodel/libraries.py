from complexism.abmodel.network import *
# from complexism.abmodel.traits import *
from complexism.abmodel.be import *
from epidag.factory import get_workshop
import epidag.factory.arguments as vld
import logging

__author__ = 'TimeWz667'
__all__ = []


logger = logging.getLogger(__name__)

# Network library
NetworkLibrary = get_workshop('Networks')
NetworkLibrary.register('BA', NetworkBA, [vld.PositiveInteger('m')])
NetworkLibrary.register('GNP', NetworkGNP, [vld.Prob('p')])
NetworkLibrary.register('Category', NetworkProb, [vld.Prob('p')])
logger.info('Network library (Networks) loaded')

# Trait library
# TraitLibrary = get_workshop('Traits')
# TraitLibrary.register('Binary', TraitBinary, [vld.Prob('prob'), vld.List('tf', 2)])
# TraitLibrary.register('Distribution', TraitDistribution, [vld.RegExp('dist', r'\w+\(')])
# TraitLibrary.register('Category', TraitCategory, [vld.ProbTab('kv')])
# logger.info('Trait library (Traits) loaded')

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
BehaviourLibrary.register('ComFDShock', ComFDShock,
                          [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states')])
BehaviourLibrary.register('ComFDShockFast', ComFDShockFast,
                          [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                           vld.PositiveFloat('dt', opt=True, default=0.5)])
BehaviourLibrary.register('ComDDShock', ComDDShock,
                          [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states')])
BehaviourLibrary.register('ComDDShockFast', ComDDShockFast,
                          [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                           vld.PositiveFloat('dt', opt=True, default=0.5)])
BehaviourLibrary.register('NerfDecision', NerfDecision,
                          [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'), vld.Prob('prob')])
BehaviourLibrary.register('BuffDecision', BuffDecision,
                          [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'), vld.Prob('prob')])
BehaviourLibrary.register('ComWeightSumShock', ComWeightSumShock,
                          [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                           vld.ProbTab('weight'), vld.PositiveFloat('dt', opt=True, default=0.5)])
BehaviourLibrary.register('ComWeightAvgShock', ComWeightAvgShock,
                          [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                           vld.ProbTab('weight'), vld.PositiveFloat('dt', opt=True, default=0.5)])
BehaviourLibrary.register('NetShock', NetShock,
                          [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                           vld.Options('net', 'networks')])
BehaviourLibrary.register('NetWeightShock', NetWeightShock,
                          [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                           vld.Options('net', 'networks'), vld.ProbTab('weight')])
BehaviourLibrary.register('TimeStep', TimeStep,
                          [vld.Options('t_tar', 'transitions'), vld.List('ys'), vld.List('ts')])
BehaviourLibrary.register('ForeignShock', ForeignShock,
                          [vld.Options('t_tar', 'transitions'), vld.String('mod_src', opt=True), vld.String('mod_src', opt=True)])

logger.info('ABM Behaviour library (ABM_BE) loaded')


if __name__ == '__main__':
    print(NetworkLibrary.get_form('BA'))
    print(TraitLibrary.get_form('Binary'))
