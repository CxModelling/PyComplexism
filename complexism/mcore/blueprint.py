from abc import ABCMeta, abstractstaticmethod, abstractmethod

__author__ = 'TimeWz667'


class AbsBlueprintMCore(metaclass=ABCMeta):
    def __init__(self, name):
        self.Name = name
        self.Arguments = dict()
        self.__pc = None

    def set_arguments(self, key, value):
        if key in self.Arguments:
            self.Arguments[key] = value

    def get_arguments(self, key):
        return self.Arguments[key]

    def link_to_pc(self, pc):
        """
        Link the model to a specific parameter model
        :param pc: pc
        :type pc: str
        """
        self.__pc = pc

    @abstractmethod
    def get_parameter_hierarchy(self, **kwargs):
        pass

    @property
    def require_pc(self):
        return bool(self.__pc)

    @property
    def TargetedPCore(self):
        return self.__pc

    @abstractmethod
    def generate(self, name, **kwargs):
        pass

    @abstractmethod
    def to_json(self):
        pass

    @abstractmethod
    def clone(self, mod_src, **kwargs):
        pass

    @abstractstaticmethod
    def from_json(self, js):
        pass
