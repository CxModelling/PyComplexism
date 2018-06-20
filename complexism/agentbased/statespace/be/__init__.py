from epidag.factory import get_workshop
import epidag.factory.arguments as vld

from .trigger import *
from .behaviour import *
from .modbe import *
from .lifebe import *
# from .listener import *

__author__ = 'TimeWz667'
__all__ = ['PassiveModBehaviour', 'ActiveModBehaviour',
           'TransitionTrigger', 'StateTrigger', 'StateEnterTrigger', 'StateExitTrigger',
           'FDShock', 'FDShockFast', 'DDShock', 'DDShockFast',
           'WeightSumShock', 'WeightAvgShock', 'NetShock', 'NetWeightShock',
           'SwitchOn', 'SwitchOff',
           'Reincarnation', 'Cohort', 'LifeRate', 'LifeS', 'AgentImport',
           'StSpBeLibrary']


StSpBeLibrary = get_workshop('StSpABM_BE')

StSpBeLibrary.register('Cohort', Cohort, [vld.Options('s_death', 'states')])
StSpBeLibrary.register('Reincarnation', Reincarnation,
                       [vld.Options('s_death', 'states'), vld.Options('s_birth', 'states')])
StSpBeLibrary.register('LifeRate', LifeRate,
                       [vld.Options('s_death', 'states'), vld.Options('s_birth', 'states'),
                        vld.PositiveFloat('rate'), vld.PositiveFloat('dt', opt=True, default=0.5)])
StSpBeLibrary.register('LifeS', LifeS,
                       [vld.Options('s_death', 'states'), vld.Options('s_birth', 'states'),
                        vld.PositiveFloat('rate'), vld.PositiveFloat('cap'),
                        vld.PositiveFloat('dt', opt=True, default=0.5)])

StSpBeLibrary.register('FDShock', FDShock,
                       [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states')])
StSpBeLibrary.register('FDShockFast', FDShockFast,
                       [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                           vld.PositiveFloat('dt', opt=True, default=0.5)])
StSpBeLibrary.register('DDShock', DDShock,
                       [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states')])
StSpBeLibrary.register('DDShockFast', DDShockFast,
                       [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                        vld.PositiveFloat('dt', opt=True, default=0.5)])
StSpBeLibrary.register('SwitchOff', SwitchOff,
                       [vld.Options('t_tar', 'transitions'),
                        vld.Options('s_src', 'states'),
                        vld.Prob('prob')])
StSpBeLibrary.register('SwitchOn', SwitchOn,
                       [vld.Options('t_tar', 'transitions'),
                        vld.Options('s_src', 'states'),
                        vld.Prob('prob')])
StSpBeLibrary.register('WeightSumShock', WeightSumShock,
                       [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                        vld.ProbTab('weight'), vld.PositiveFloat('dt', opt=True, default=0.5)])
StSpBeLibrary.register('WeightAvgShock', WeightAvgShock,
                       [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                        vld.ProbTab('weight'), vld.PositiveFloat('dt', opt=True, default=0.5)])
StSpBeLibrary.register('NetShock', NetShock,
                       [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                        vld.Options('net', 'networks')])
StSpBeLibrary.register('NetWeightShock', NetWeightShock,
                       [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                        vld.Options('net', 'networks'), vld.ProbTab('weight')])

# StSpBeLibrary.register('ForeignShock', ForeignShock,
#                       [vld.Options('t_tar', 'transitions'),
#                        vld.String('mod_src', opt=True),
#                        vld.String('par_src', opt=True),
#                        vld.PositiveFloat('default', default=1, opt=True)])

# StSpBeLibrary.register('ForeignSumShock', ForeignSumShock,
#                        [vld.Options('t_tar', 'transitions'),
#                         vld.NotNull('mod_par_src', opt=True),
#                         vld.PositiveFloat('default', default=1, opt=True)])

StSpBeLibrary.register('AgentImport', AgentImport,
                       [vld.Options('s_birth', 'states')])
