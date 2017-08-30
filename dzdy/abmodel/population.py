from dzdy.abmodel import Agent, NetworkSet, TraitSet
import pandas as pd
from collections import OrderedDict


class Breeder:
    def __init__(self, sts, prefix='Ag'):
        self.Last = 0
        self.Prefix = prefix
        self.States = sts
        self.Traits = TraitSet()

    def breed(self, st, n=1, info=None):
        try:
            st = self.States[st]
        except KeyError:
            raise KeyError('The state is not well-defined')
        info = info if info else dict()
        start = self.Last + 1
        ags = [Agent('{}{}'.format(self.Prefix, start + i), st) for i in range(n)]
        for ag in ags:
            ag.update_info(info)
            self.Traits(ag.Info)

        self.Last += n
        return ags

    def append_trait(self, trait):
        self.Traits.append(trait)


class Population:
    def __init__(self, core, prefix='Ag'):
        self.Eve = Breeder(core.get_state_space(), prefix)
        self.Agents = OrderedDict()
        self.Networks = NetworkSet()

    def __getitem__(self, item):
        try:
            return self.Agents[item]
        except KeyError:
            raise KeyError('No this agent')

    def append_trait(self, fi):
        self.Eve.Traits.append(fi)

    def add_network(self, net):
        self.Networks[net.Name] = net

    def count(self, st=None):
        """
        count agents with a certain state
        Args:
            st: target state or name of state

        Returns: number

        """
        if st:
            if isinstance(st, str):
                st = self.Eve.States[st]
            return sum(st in ag for ag in self.Agents.values())
        else:
            return len(self.Agents)

    def neighbours(self, ag, net='|'):
        if net == '|':
            return self.Networks.neighbours_of(ag)
        elif net == '*':
            return self.Networks.neighbour_set_of(ag)
        else:
            try:
                return self.Networks.neighbours_of(ag, net)
            except KeyError:
                raise KeyError('No this net')

    def count_neighbours(self, ag, st=None, net=None):
        nes = self.neighbours(ag, net=net)
        if st:
            return sum(st in nei for nei in nes)
        else:
            return len(list(nes))

    def get_info_table(self):
        """
        get a pd.DataFrame table of the information of agents
        Returns: pd.DataFrame table

        """
        return pd.DataFrame.from_records([ag.Info for ag in self.Agents.values()])

    def add_agent(self, atr, n=1, info=None):
        """
        Add agents
        Args:
            atr: either the name of the attribute or entity of the attribute
            n: the number of agents need to be generate
            info: a dict of info. eg. {'Sex': 'F', 'Age': 26}

        Returns: a list of generated agents

        """
        ags = self.Eve.breed(atr, n, info)
        ags = list(ags)
        for ag in ags:
            self.Agents[ag.Name] = ag
            self.Networks.add_agent(ag)
        return ags

    def remove_agent(self, i):
        """
        Remove agent from population, disconnecting all social links around it
        Args:
            i: string, name of agent

        Returns: the deleted agent

        """
        try:
            ag = self[i]
            del self.Agents[i]
            self.Networks.remove_agent(ag)
        except KeyError:
            raise KeyError('No this agent')
        return ag

    def reform(self, net=None):
        self.Networks.reform(net)

    def first(self, n=5):
        for k, v in self.Agents.items():
            if n > 0:
                yield v
            else:
                return
            n -= 1

    def __str__(self):
        return "Population Size: {}\nNetwork: \n{}".format(len(self.Agents), repr(self.Networks))

    def __repr__(self):
        return "Population Size: {}, Network: {}".format(len(self.Agents), str(self.Networks))
