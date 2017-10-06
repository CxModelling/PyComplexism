import dzdy.validators as vld
from dzdy.ebmodel.behaviour import *
import logging
from collections import namedtuple

__author__ = 'TimeWz667'

__all__ = ['register_behaviour', 'validate_behaviour',
           'get_behaviour', 'get_behaviour_from_json',
           'get_behaviour_template', 'get_behaviour_defaults',
           'install_behaviour_from_json', 'install_behaviour', 'BehaviourLibrary']

log = logging.getLogger(__name__)


Entry = namedtuple('Entry', ('Class', 'Options'))

# Network library
BehaviourLibrary = dict()


def register_behaviour(be_type, cls, vls):
    opts = vld.Options()
    for k, vl in vls.items():
        opts.append(k, vl)
    BehaviourLibrary[be_type] = Entry(cls, opts)


def validate_behaviour(be_type, kwargs):
    opts = BehaviourLibrary[be_type].Options
    return opts.check_all(kwargs, log=log)


def get_behaviour(be_name, be_type, kwargs):
    be = BehaviourLibrary[be_type]
    if be.Options.modify(kwargs, log):
        kwargs = be.Options.extract(kwargs, log)
        return be.Class(be_name, **kwargs)


def get_behaviour_from_json(js):
    tp = js['Type']
    be = BehaviourLibrary[tp]
    return be.from_json(js)


def get_behaviour_template(be_type):
    return BehaviourLibrary[be_type].Options.get_form()


def get_behaviour_defaults(be_type):
    return BehaviourLibrary[be_type].Options.get_defaults()


def install_behaviour(mod, be_name, be_type, kwargs):
    be = get_behaviour(be_name, be_type, kwargs)
    mod.ODE.add_behaviour(be)


def install_behaviour_from_json(mod, js):
    name = js['Name']
    tp = js['Type']
    net = get_behaviour(name, tp, js)
    if net:
        mod.Pop.add_network(net)


def list_behaviours():
    return list(BehaviourLibrary.keys())


register_behaviour('Multiplier', Multiplier,
               {'t_tar': vld.Existence()})
register_behaviour('InfectionFD', InfectionFD,
               {'t_tar': vld.Existence(), 's_src': vld.Existence()})
register_behaviour('InfectionDD', InfectionDD,
               {'t_tar': vld.Existence(), 's_src': vld.Existence()})
register_behaviour('Cohort', Cohort,
               {'s_death': vld.Existence()})
register_behaviour('Reincarnation', Reincarnation,
               {'s_death': vld.Existence(), 's_birth': vld.Existence()})

register_behaviour('DemoDynamic', DemoDynamic,
               {'s_death': vld.Existence(), 's_birth': vld.Existence(),
                't_death': vld.Existence(), 'demo': vld.Existence()})
