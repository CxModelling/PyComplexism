from epidag.factory import get_workshop
import epidag.factory.arguments as vld

from .trigger import *
from .behaviour import *
from .modbe import *
from .lifebe import *
from .publisher import *

__author__ = 'TimeWz667'
__all__ = ['PassiveModBehaviour', 'ActiveModBehaviour',
           'TransitionTrigger', 'StateTrigger', 'StateEnterTrigger', 'StateExitTrigger',
           'ExternalShock',
           'FDShock', 'FDShockFast', 'DDShock', 'DDShockFast',
           'WeightedSumShock', 'WeightedAvgShock', 'NetShock', 'NetWeightShock',
           'SwitchOn', 'SwitchOff',
           'Reincarnation', 'Cohort', 'LifeRate', 'LifeS', 'AgentImport',
           'BirthAgeingDeathLeeCarter',
           'StateTrack',
           'register_behaviour']

StSpBeLibrary = get_workshop('StSpABM_BE')


def register_behaviour(tp, obj, args):
    StSpBeLibrary.register(tp, obj, args, meta=['Name'])


register_behaviour('Cohort', Cohort, [vld.Options('s_death', 'states')])

StSpBeLibrary.register('Cohort', Cohort, [vld.Options('s_death', 'states')], meta=['Name'])
register_behaviour('Reincarnation', Reincarnation,
                   [vld.Options('s_death', 'states'), vld.Options('s_birth', 'states')])
register_behaviour('LifeRate', LifeRate,
                   [vld.Options('s_death', 'states'), vld.Options('s_birth', 'states'),
                    vld.PositiveFloat('rate'), vld.PositiveFloat('dt', opt=True, default=0.5)])
register_behaviour('LifeS', LifeS,
                   [vld.Options('s_death', 'states'), vld.Options('s_birth', 'states'),
                    vld.PositiveFloat('rate'), vld.PositiveFloat('cap'),
                    vld.PositiveFloat('dt', opt=True, default=0.5)])

register_behaviour('StateTrack', StateTrack,
                   [vld.Options('s_src', 'states')])

register_behaviour('ExternalShock', ExternalShock,
                   [vld.Options('t_tar', 'transitions')])

register_behaviour('FDShock', FDShock,
                   [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states')])
register_behaviour('FDShockFast', FDShockFast,
                   [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                    vld.PositiveFloat('dt', opt=True, default=0.5)])
register_behaviour('DDShock', DDShock,
                   [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states')])
register_behaviour('DDShockFast', DDShockFast,
                   [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                    vld.PositiveFloat('dt', opt=True, default=0.5)])
register_behaviour('SwitchOff', SwitchOff,
                   [vld.Options('t_tar', 'transitions'),
                    vld.Options('s_src', 'states'),
                    vld.Prob('prob')])
register_behaviour('SwitchOn', SwitchOn,
                   [vld.Options('t_tar', 'transitions'),
                    vld.Options('s_src', 'states'),
                    vld.Prob('prob')])
register_behaviour('WeightedSumShock', WeightedSumShock,
                   [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                    vld.ProbTab('weight'), vld.PositiveFloat('dt', opt=True, default=0.5)])
register_behaviour('WeightedAvgShock', WeightedAvgShock,
                   [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                    vld.ProbTab('weight'), vld.PositiveFloat('dt', opt=True, default=0.5)])
register_behaviour('NetShock', NetShock,
                   [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                    vld.Options('net', 'networks')])
register_behaviour('NetWeightShock', NetWeightShock,
                   [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                    vld.Options('net', 'networks'), vld.ProbTab('weight')])

register_behaviour('AgentImport', AgentImport, [vld.Options('s_birth', 'states')])

register_behaviour('BirthAgeingDeathLeeCarter', BirthAgeingDeathLeeCarter,
                   [vld.Options('s_death', 'states'),
                    vld.Options('t_die', 'transitions'),
                    vld.Options('s_birth', 'states'),
                    vld.NotNull('dlc')
                   ])
