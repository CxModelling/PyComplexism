from epidag.factory import get_workshop
import epidag.factory.arguments as vld

from .trigger import *
from .behaviour import *
from .modbe import *
# from .lifebe import *
# from .listener import *

__author__ = 'TimeWz667'
__all__ = ['TimeIndModBehaviour', 'TimeDepModBehaviour',
           'TransitionTrigger', 'StateTrigger', 'StateEnterTrigger', 'StateExitTrigger',
           'FDShock', 'FDShockFast', 'DDShock', 'DDShockFast',
           'StSpBeLibrary']


StSpBeLibrary = get_workshop('ABM_BE')

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
