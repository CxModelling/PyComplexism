import dzdy.validators as vld
from dzdy.abmodel.network import *
from dzdy.abmodel.traits import *
import logging

from collections import namedtuple

__author__ = 'TimeWz667'

__all__ = ['register_network', 'get_network', 'install_network',
           'get_network_template', 'get_network_defaults']

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


def get_network(net_type, kwargs):
    return NetworkLibrary[net_type].Class(**kwargs)




def get_network_template(net_type):
    return NetworkLibrary[net_type].Options.get_form()


def get_network_defaults(net_type):
    return NetworkLibrary[net_type].Options.get_defaults()


def install_network(mod, net_name, net_type, kwargs):
    net = get_network(net_type, kwargs)
    mod.Pop.add_network(net_name, net)


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


def get_trait(trait_type, kwargs):
    return TraitsLibrary[trait_type].Class(**kwargs)

def get_trait_js(js):
    return TraitsLibrary[js['Type']].from_json(js)


def get_trait_template(trait_type):
    return TraitsLibrary[trait_type].Options.get_form()


def get_trait_defaults(trait_type):
    return NetworkLibrary[trait_type].Options.get_defaults()




def install_trait(mod, js):
    """

    Args:
        mod (AgentBasedModel):
        js (dict): json of trait definition

    """
    trait = get_trait(js)
    mod.Pop.add_trait(trait)


def list_traits():
    return list(TraitsLibrary.keys())


register_network('BA', NetworkBA, {'m': vld.Number(lower=0, is_float=False)})
register_network('GNP', NetworkGNP, {'p': vld.Number(lower=0, upper=1)})


register_trait('Binary', TraitBinary, )
register_trait('Distribution', TraitDistribution)
register_trait('Category', TraitCategory)




if __name__ == '__main__':
    print(get_network_template('BA'))

