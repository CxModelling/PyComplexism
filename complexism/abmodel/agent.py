from complexism.mcore import ModelAtom
from abc import ABCMeta, abstractmethod

__author__ = 'TimeWz667'


class GenericAgent(ModelAtom, metaclass=ABCMeta):
    def __init__(self, name, pars=None):
        ModelAtom.__init__(self, name, pars)

    def __repr__(self):
        s = 'ID: {}, '.format(self.Name)
        s += ', '.join(['{}: {}'.format(k, v) for k, v in self.Attributes.items()])
        return s

    @abstractmethod
    def update_time(self, time):
        """
        Update status to the current time
        :param time: current time
        :type time: float
        """
        pass
