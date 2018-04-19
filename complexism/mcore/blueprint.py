from abc import ABCMeta, abstractstaticmethod, abstractmethod

__author__ = 'TimeWz667'


class AbsBlueprintMCore(metaclass=ABCMeta):
    def __init__(self, name, args, pc, dc):
        self.Name = name
        self.Arguments = args
        self.__pc = pc
        self.__dc = dc

    def set_arguments(self, key, value):
        if key in self.Arguments:
            self.Arguments[key] = value

    def get_arguments(self, key):
        return self.Arguments

    @property
    def require_pc(self):
        return bool(self.__pc)

    @property
    def require_dc(self):
        return bool(self.__dc)

    @property
    def TargetedPCore(self):
        return self.__pc

    @property
    def TargetedDCore(self):
        return self.__dc

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
    def from_json(self):
        pass
