from dzdy.abmodel.network import *
from dzdy.abmodel.traits import *
from factory.manager import ResourceManager
import factory.arguments as vld

import logging


__author__ = 'TimeWz667'

__all__ = [
            'NetworkLibrary', 'get_network_from_json',
            'get_network_template', 'install_network_from_json', 'install_network',
            'TraitLibrary', 'get_trait_from_json',
            'get_trait_template', 'install_trait_from_json', 'install_trait',
           ]

logger = logging.getLogger(__name__)

# Network library
NetworkLibrary = ResourceManager()
NetworkLibrary.register('BA', NetworkBA, [vld.PositiveInteger('m')])
NetworkLibrary.register('GNP', NetworkGNP, [vld.Prob('p')])
NetworkLibrary.register('Category', NetworkProb, [vld.Prob('p')])


def get_network_from_json(js):
    return NetworkLibrary.create(js, logger)


def get_network_template(net_type):
    return NetworkLibrary.get_form(net_type)


def install_network_from_json(mod, js):
    net = get_network_from_json(js)
    if net:
        mod.Pop.add_network(net)


def install_network(mod, net_name, net_type, net_args):
    install_network_from_json(mod, {'Name': net_name, 'Type': net_type, 'Args': net_args})


def list_networks():
    return NetworkLibrary.list()


TraitLibrary = ResourceManager()
TraitLibrary.register('Binary', TraitBinary, [vld.Prob('prob'), vld.ListString('tf', 2)])
TraitLibrary.register('Distribution', TraitDistribution, [vld.RegExp('dist', r'\w+\(')])
TraitLibrary.register('Category', TraitCategory, [vld.ProbTab('kv')])


def get_trait_from_json(js):
    return TraitLibrary.create(js, logger)


def get_trait_template(trait_type):
    return TraitLibrary.get_form(trait_type)


def install_trait_from_json(mod, js):
    trait = get_trait_from_json(js)
    mod.Pop.add_trait(trait)


def install_trait(mod, trt_name, trt_type, trt_args):
    install_trait_from_json(mod, {'Name': trt_name, 'Type': trt_type, 'Args': trt_args})


def list_traits():
    return TraitLibrary.list()


if __name__ == '__main__':
    print(get_network_template('BA'))
    print(get_trait_template('Binary'))
