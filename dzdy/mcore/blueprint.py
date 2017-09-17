from abc import ABCMeta, abstractstaticmethod, abstractmethod

__author__ = 'TimeWz667'


class AbsBlueprintMCore(metaclass=ABCMeta):
    def __init__(self, name, args):
        self.Name = name
        self.Arguments = args

    def set_arguments(self, key, value):
        if key in self.Arguments:
            self.Arguments[key] = value

    def get_arguments(self, key):
        return self.Arguments

    @property
    def require_pc(self):
        return True

    @property
    def require_dc(self):
        return True

    @property
    def TargetedPCore(self):
        return None

    @property
    def TargetedDCore(self):
        return None

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
