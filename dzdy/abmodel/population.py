from dzdy.abmodel import Agent, NetworkBA, NetworkSet, FillUpSet
import pandas as pd
from collections import OrderedDict


class Breeder:
    def __init__(self, sts, prefix='Ag'):
        self.Last = 0
        self.Prefix = prefix
        self.States = sts
        self.Fill = FillUpSet()

    def breed(self, st, n=1, info=None):
        try:
            st = self.States[st]
        except KeyError:
            raise KeyError('It is not a well-defined State')
        info = info if info else dict()
        start = self.Last + 1
        ags = [Agent('{}{}'.format(self.Prefix, start + i), st) for i in range(n)]
        for ag in ags:
            ag.update_info(self.Fill(info.copy()))
        self.Last += n
        return ags

    def breed_multi(self, di):
        for d in di:
            if 'info' not in d:
                d['info'] = dict()
            for ag in self.breed(d['st'], d['n'], d['info']):
                yield ag


class Population:
    def __init__(self, core, prefix='Ag'):
        self.Eve = Breeder(core.get_state_space(), prefix)
        self.Agents = OrderedDict()

    def __getitem__(self, item):
        try:
            return self.Agents[item]
        except KeyError:
            raise KeyError('No this agent')

    def append_fill(self, fi):
        self.Eve.Fill.append(fi)

    def count(self, st=None):
        if st:
            return sum(st in ag for ag in self.Agents.values())
        else:
            return len(self.Agents)

    def neighbours(self, ag, **kwargs):
        if isinstance(ag, str):
            ag = self.Agents[ag]
        return (nei for nei in self.Agents.values() if nei is not ag)

    def count_neighbours(self, ag, st=None, net=None):
        nes = self.neighbours(ag, net=net)
        if st:
            return sum(st in nei for nei in nes)
        else:
            return len(list(nes))

    def get_info_table(self):
        """
        get a pd.DataFrame table of the information of agents
        :return: pd.DataFrame table
        """
        return pd.DataFrame.from_records([ag.Info for ag in self.Agents.values()])

    def add_agent(self, atr, n=1, info=None):
        """

        :param atr: either the name of the attribute or entity of the attribute
        :param n: the number of agents need to be generate
        :param info: a dict of info. eg. {'Sex': 'F', 'Age': 26 }
        :return: a list of generated agents
        """
        ags = self.Eve.breed(atr, n, info)
        ags = list(ags)
        for ag in ags:
            self.Agents[ag.Name] = ag
        return ags

    def remove_agent(self, i):
        """
        remove agent from population, disconnecting all social links around it
        :param i: string, name of agent
        :return: deleted agent
        """
        try:
            ag = self[i]
            del self.Agents[i]
        except KeyError:
            raise KeyError('No this agent')
        return ag

    def reform(self, **kwargs):
        return

    def first(self, n=5):
        for k, v in self.Agents.items():
            if n > 0:
                yield v
            else:
                return
            n -= 1

    def __repr__(self):
        return "Population Size: {}\nNetwork: CompleteNet".format(len(self.Agents))

    @staticmethod
    def decorate(model, **kwargs):
        model.Pop = Population(model.DCore, **kwargs)

    __str__ = __repr__


class NetworkPopulation(Population):
    def __init__(self, core, prefix='Ag', net=None):
        Population.__init__(self, core, prefix)
        self.Network = net if net else NetworkBA(2)

    def neighbours(self, ag, **kwargs):
        if not isinstance(ag, Agent):
            ag = self.Agents[ag]
        try:
            return self.Network[ag]
        except KeyError:
            return []

    def add_agent(self, st, n=1, info=None):
        ags = Population.add_agent(self, st, n, info)
        for ag in ags:
            self.Network.add_agent(ag)
        return ags

    def remove_agent(self, i):
        ag = Population.remove_agent(self, i)
        self.Network.remove_agent(ag)
        return ag

    def reform(self, **kwargs):
        self.Network.reform()

    def __repr__(self):
        return "Population Size: {}\nNetwork: {}".format(len(self.Agents), self.Network)

    __str__ = __repr__

    @staticmethod
    def decorate(model, **kwargs):
        model.Pop = NetworkPopulation(model.DCore, **kwargs)


class MultilayerPopulation(Population):
    def __init__(self, core, prefix='Ag'):
        Population.__init__(self, core, prefix)
        self.Networks = NetworkSet()

    def add_network(self, name, net):
        self.Networks[name] = net

    def neighbours(self, ag, **kwargs):
        if isinstance(ag, str):
            ag = self.Agents[ag]
        if 'net' not in kwargs:
            return Population.neighbours(self, ag)
        net = kwargs['net']
        if net == '*':
            return self.Networks.neighbours_of(ag)
        if net == '|':
            return self.Networks.neighbour_set_of(ag)
        try:
            return self.Networks.neighbours_of(ag, net)
        except KeyError:
            return KeyError('No this net')

    def add_agent(self, st, n=1, info=None):
        ags = Population.add_agent(self, st, n, info)
        for ag in ags:
            self.Networks.add_agent(ag)

        return ags

    def remove_agent(self, i):
        ag = Population.remove_agent(self, i)
        self.Networks.remove_agent(ag)
        return ag

    def reform(self, **kwargs):
        self.Networks.reform(**kwargs)

    def __str__(self):
        return "Population Size: {}\nNetwork: \n{}".format(len(self.Agents), repr(self.Networks))

    def __repr__(self):
        return "Population Size: {}, Network: {}".format(len(self.Agents), str(self.Networks))

    @staticmethod
    def decorate(model, **kwargs):
        model.Pop = MultilayerPopulation(model.DCore, **kwargs)
