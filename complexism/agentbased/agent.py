from src.pycx.misc import NameGenerator
from mcore import ModelAtom
from abc import ABCMeta, abstractmethod

__author__ = 'TimeWz667'
__all__ = ['GenericAgent', 'GenericBreeder']


class GenericAgent(ModelAtom, metaclass=ABCMeta):
    def __init__(self, name, pars=None):
        ModelAtom.__init__(self, name, pars)

    def __repr__(self):
        s = 'ID: {}, '.format(self.Name)
        if self.Attributes:
            s += ', '.join(['{}: {}'.format(k, v) for k, v in self.Attributes.items()])
        return s

    @abstractmethod
    def update_time(self, ti):
        """
        Update status to the current time
        :param ti: current time
        :type ti: float
        """
        pass


class GenericBreeder(metaclass=ABCMeta):
    def __init__(self, name, group, pc_parent, **kwargs):
        self.Name = name
        self.Group = group
        self.GenName = NameGenerator(name, 1, 1)
        self.PCore = pc_parent.get_prototype(group)
        self.Exo = kwargs

    def breed(self, n=1, **kwargs):
        """
        Breed new agents
        :param n: population size to breed
        :param kwargs: attributes to be attached
        :return: a list of new agents
        :rtype: list
        """
        sts, ats = self._filter_attributes(kwargs)

        ags = list()
        for i in range(int(n)):
            name = self.GenName.get_next()
            pars = self.PCore.get_sibling(name, self.Exo)
            ag = self._new_agent(name, pars, **sts)
            ag.Attributes.update(ats)
            ags.append(ag)
        return ags

    @abstractmethod
    def _filter_attributes(self, kw):
        """
        Separate status from attributes
        :param kw: keyword arguments
        :return: status, attributes
        :rtype: (dict, dict)
        """
        pass

    @abstractmethod
    def _new_agent(self, name, pars, **kwargs):
        pass
