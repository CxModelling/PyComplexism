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
           'StSpBeLibrary']


StSpBeLibrary = get_workshop('ABM_BE')


StSpBeLibrary.register('ComFDShock', ComFDShock,
                       [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states')])
StSpBeLibrary.register('ComFDShockFast', ComFDShockFast,
                       [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                           vld.PositiveFloat('dt', opt=True, default=0.5)])
StSpBeLibrary.register('ComDDShock', ComDDShock,
                       [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states')])
StSpBeLibrary.register('ComDDShockFast', ComDDShockFast,
                       [vld.Options('t_tar', 'transitions'), vld.Options('s_src', 'states'),
                        vld.PositiveFloat('dt', opt=True, default=0.5)])
