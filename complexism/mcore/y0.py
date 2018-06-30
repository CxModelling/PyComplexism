from abc import ABCMeta, abstractmethod

__all__ = ['LeafY0', 'BranchY0']


class AbsY0(metaclass=ABCMeta):
    @abstractmethod
    def match_model(self, model):
        pass

    @abstractmethod
    def define(self, *args, **kwargs):
        pass

    @staticmethod
    @abstractmethod
    def from_source(src):
        pass


class LeafY0(AbsY0, metaclass=ABCMeta):
    pass


class BranchY0(AbsY0, metaclass=ABCMeta):
    def __init__(self):
        self.ChildrenY0 = dict()

    @abstractmethod
    def append_child(self, key, chd):
        self.ChildrenY0[key] = chd
