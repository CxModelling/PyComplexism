from .population import Population
from .network import NetworkSet

__author__ = 'TimeWz667'
__all__ = ['Community']


class Community(Population):
    def __init__(self, breeder):
        Population.__init__(self, breeder)
        self.Networks = NetworkSet()

    def add_network(self, net):
        self.Networks[net.Name] = net

    def neighbours(self, ag, net='|'):
        """
        Find the neighbours of an agent given a network layer
        :param ag: agent
        :type ag: str or GenericAgent
        :param net: name of network; '|' for all networks in dict; '*' for neighbours in all networks
        :return:
        """
        if isinstance(ag, str):
            try:
                ag = self.Agents[ag]
            except KeyError:
                raise KeyError('No this agent')

        if net == '|':
            return self.Networks.neighbours_of(ag)
        elif net == '*':
            return self.Networks.neighbour_set_of(ag)
        else:
            try:
                return self.Networks.neighbours_of(ag, net)
            except KeyError:
                raise KeyError('No this net')

    def count_neighbours(self, ag, net=None, **kwargs):
        nes = self.neighbours(ag, net=net)
        if isinstance(nes, list):
            return self.Eve.count(nes, **kwargs)
        elif isinstance(nes, dict):
            return {k: self.Eve.count(v, **kwargs) for k, v in nes.items()}
        else:
            return 0

    def reform_networks(self, net=None):
        """
        Reform networks
        :param net: name of network; blink for all networks
        """
        self.Networks.reform(net)
