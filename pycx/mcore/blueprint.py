from abc import ABCMeta, abstractmethod

__author__ = 'TimeWz667'
__all__ = ['AbsModelBlueprint']


class AbsModelBlueprint(metaclass=ABCMeta):
    def __init__(self, name):
        self.Class = name
        self.Arguments = dict()
        self.__bn = None

    def set_arguments(self, key, value):
        if key in self.Arguments:
            self.Arguments[key] = value

    def get_arguments(self, key):
        return self.Arguments[key]

    def link_to_bn(self, bn):
        """
        Link the model to a specific bayesian network parameter model
        :param bn: new of a Bayesian network
        :type bn: str
        """
        self.__bn = bn

    @abstractmethod
    def get_parameter_hierarchy(self, **kwargs):
        pass

    @abstractmethod
    def get_y0_proto(self):
        pass

    def get_y0s(self, da=None):
        return self.get_y0_proto()

    @property
    def requires_bn(self):
        return bool(self.__bn)

    @property
    def target_bn(self):
        return self.__bn

    @abstractmethod
    def generate(self, name, **kwargs):
        pass

    @abstractmethod
    def to_json(self):
        pass

    @abstractmethod
    def clone_model(self, mod_src, **kwargs):
        pass

    @staticmethod
    @abstractmethod
    def from_json(js):
        pass
