from abc import ABCMeta, abstractstaticmethod, abstractmethod

__author__ = 'TimeWz667'


class AbsBlueprintMCore(metaclass=ABCMeta):
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
