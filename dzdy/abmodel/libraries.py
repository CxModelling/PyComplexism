import dzdy.validators as vld
import dzdy.abmodel.network as nw
import logging

__author__ = 'TimeWz667'

__all__ = ['register_network', 'get_network', 'install_network',
           'get_network_template', 'get_network_options']

log = logging.getLogger(__name__)

# Network library
NetworkLibrary = dict()


def register_network(net_type, cls, vlds):
    NetworkLibrary[net_type] = (cls, vlds)


def validate_network(net_type, kwargs):
    vlds = NetworkLibrary[net_type][1]
    return vld.check_all(kwargs, vlds, log=log)


def get_network(net_type, kwargs):
    return NetworkLibrary[net_type]['Type'](**kwargs)


def get_network_template(net_type):
    return {k: v.Default for k, v in NetworkLibrary[net_type][1].items()}


def get_network_options(net_type):
    return {k: v.Default for k, v in NetworkLibrary[net_type][1].items()}


def install_network(mod, net_name, net_type, kwargs):
    net = get_network(net_type, kwargs)
    mod.Pop.add_network(net_name, net)


def list_networks():
    return list(NetworkLibrary.keys())


register_network('BA', nw.NetworkBA, {'m': vld.Number(lower=0, double=False)})
register_network('GNP', nw.NetworkGNP, {'p': vld.Number(lower=0, upper=1)})
