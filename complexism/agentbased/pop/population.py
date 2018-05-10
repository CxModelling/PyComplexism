from collections import OrderedDict

__author__ = 'TimeWz667'
__all__ = ['Population']


class Population:
    def __init__(self, breeder):
        self.Eve = breeder
        self.Agents = OrderedDict()

    def __getitem__(self, item):
        try:
            return self.Agents[item]
        except KeyError:
            raise KeyError('Agent not found')

    def count(self, **kwargs):
        """
        Count how many agents are included in certain criteria
        :param kwargs: criteria for selecting agents
        :return: count number
        :rtype: int
        """
        self.Eve.count(self.Agents.values(), **kwargs)

    def add_agent(self, n=1, **kwargs):
        """
        Add agents
        :param n: number of agents to be created
        :type n: int
        :param kwargs: status or attributes of new agents
        :return: a list of new agents
        :rtype: list
        """
        n = round(n)
        ags = self.Eve.breed(n, **kwargs)
        for ag in ags:
            self.Agents[ag.Name] = ag
        return ags

    def remove_agent(self, name):
        """
        Remove agent from population, disconnecting all social links around it
        :param name: name of agent
        :type name: str
        :return: the deleted agent
        """
        try:
            ag = self[name]
            del self.Agents[name]
        except KeyError:
            raise KeyError('Agent not found')
        return ag

    def first(self, n=5):
        for v in self.Agents.values():
            if n > 0:
                yield v
            else:
                return
            n -= 1

    def __str__(self):
        return "Population Size: {}".format(len(self.Agents))

    def __repr__(self):
        return "Population Size: {}".format(len(self.Agents))
