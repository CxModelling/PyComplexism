import dzdy.validators as vld
from dzdy.abmodel.network import *
from dzdy.abmodel.traits import *
import logging

from collections import namedtuple

__author__ = 'TimeWz667'

__all__ = ['register_network', 'validate_network',
           'get_network', 'get_network_from_json',
           'get_network_template', 'get_network_defaults',
           'install_network_from_json', 'install_network',
           'register_trait', 'validate_trait',
           'get_trait', 'get_trait_from_json',
           'get_trait_template', 'get_trait_defaults',
           'install_trait_from_json', 'install_trait',
           ]

log = logging.getLogger(__name__)


Entry = namedtuple('Entry', ('Class', 'Options'))

# Network library
NetworkLibrary = dict()


def register_network(net_type, cls, vls):
    opts = vld.Options()
    for k, vl in vls.items():
        opts.append(k, vl)
    NetworkLibrary[net_type] = Entry(cls, opts)


def validate_network(net_type, kwargs):
    opts = NetworkLibrary[net_type].Options
    return opts.check_all(kwargs, log=log)


def get_network(net_name, net_type, kwargs):
    net = NetworkLibrary[net_type]
    if net.Options.modify(kwargs, log):
        kwargs = net.Options.extract(kwargs, log)
        return net.Class(net_name, **kwargs)


def get_network_from_json(js):
    tp = js['Type']
    net = NetworkLibrary[tp]
    return net.from_json(js)


def get_network_template(net_type):
    return NetworkLibrary[net_type].Options.get_form()


def get_network_defaults(net_type):
    return NetworkLibrary[net_type].Options.get_defaults()


def install_network(mod, net_name, net_type, kwargs):
    net = get_network(net_name, net_type, kwargs)
    mod.Pop.add_network(net)


def install_network_from_json(mod, js):
    name = js['Name']
    tp = js['Type']
    net = get_network(name, tp, js)
    if net:
        mod.Pop.add_network(net)


def list_networks():
    return list(NetworkLibrary.keys())


TraitsLibrary = dict()


def register_trait(trait_type, cls, vls):
    opts = vld.Options()
    for k, vl in vls.items():
        opts.append(k, vl)
        TraitsLibrary[trait_type] = Entry(cls, opts)


def validate_trait(trait_type, kwargs):
    opts = TraitsLibrary[trait_type].Options
    return opts.check_all(kwargs, log=log)


def get_trait(trait_name, trait_type, kwargs):
    trait = TraitsLibrary[trait_type]
    if trait.Options.modify(kwargs, log):
        kwargs = trait.Options.extract(kwargs, log)
        return trait.Class(trait_name, **kwargs)


def get_trait_from_json(js):
    tp = js['Type']
    trait = TraitsLibrary[tp]
    if trait.Options.modify(js, log):
        return trait.Class.from_json(js)


def get_trait_template(trait_type):
    return TraitsLibrary[trait_type].Options.get_form()


def get_trait_defaults(trait_type):
    return NetworkLibrary[trait_type].Options.get_defaults()


def install_trait(mod, trait_name, trait_type, kwargs):
    """

    Args:
        mod: a simulation model
        trait_name: name of trait
        trait_type: type of trait
        kwargs: options of the selected trait

    """
    trait = get_trait(trait_name, trait_type, kwargs)
    mod.Pop.add_trait(trait)


def install_trait_from_json(mod, js):
    """

    Args:
        mod: a simulation model
        js: json of trait definition

    """
    trait = get_trait_from_json(js)
    mod.Pop.add_trait(trait)


def list_traits():
    return list(TraitsLibrary.keys())


register_network('BA', NetworkBA, {'m': vld.Number(lower=0, is_float=False)})
register_network('GNP', NetworkGNP, {'p': vld.Number(lower=0, upper=1)})


register_trait('Binary', TraitBinary,
               {'prob': vld.Number(0, 1, is_float=True), 'tf': vld.ListSize(2)})
register_trait('Distribution', TraitDistribution,
               {'dist': vld.RegExp(r'\w+\(', default='exp(1.0)')})
register_trait('Category', TraitCategory, {'kv': vld.ProbTab()})


if __name__ == '__main__':
    print(get_network_template('BA'))
    print(get_trait_template('Binary'))
