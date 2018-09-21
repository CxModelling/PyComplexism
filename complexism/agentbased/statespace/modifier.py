from abc import abstractmethod, ABCMeta
from collections import OrderedDict

__author__ = 'TimeWz667'


class AbsModifier(metaclass=ABCMeta):
    def __init__(self, tar, val=float('inf')):
        self.__target = tar
        self.Value = val

    @property
    def Target(self):
        return self.__target

    @abstractmethod
    def modify(self, tte):
        pass

    @abstractmethod
    def update(self, **kwargs):
        pass

    def __repr__(self):
        return 'Mod on {}'.format(self.__target.Name)

    @abstractmethod
    def clone(self):
        pass


class DirectModifier(AbsModifier):
    def __init__(self, tar, val=float('inf')):
        AbsModifier.__init__(self, tar, val)

    def modify(self, tte):
        if self.Value <= 0:
            return float('inf')
        return self.Value

    def update(self, value, **kwargs):
        if self.Value is not value:
            self.Value = value
            return True
        else:
            return False

    def clone(self):
        return DirectModifier(self.Target, self.Value)


class LocRateModifier(AbsModifier):
    def __init__(self,  tar, val=float('inf')):
        AbsModifier.__init__(self, tar, val)

    def modify(self, tte):
        if self.Value <= 0:
            return float('inf')

        return tte/self.Value

    def update(self, value, **kwargs):
        if self.Value is not value:
            self.Value = value
            return True
        else:
            return False

    def clone(self):
        return LocRateModifier(self.Target, self.Value)


class GloRateModifier(AbsModifier):
    def __init__(self, tar):
        AbsModifier.__init__(self, tar)

    def modify(self, tte):
        if self.Value <= 0:
            return float('inf')

        return tte/self.Value

    def update(self, value, **kwargs):
        if self.Value is not value:
            self.Value = value
            return True
        else:
            return False

    def clone(self):
        return self


class NerfModifier(AbsModifier):
    def __init__(self, tar, val=False):
        AbsModifier.__init__(self, tar, val)

    def modify(self, tte):
        if self.Value:
            return float('inf')
        else:
            return tte

    def update(self, value, **kwargs):
        val = bool(value)
        if self.Value ^ val:
            self.Value = val
            return True
        else:
            return False

    def clone(self):
        return NerfModifier(self.Target, self.Value)


class BuffModifier(AbsModifier):
    def __init__(self, tar, val=True):
        AbsModifier.__init__(self, tar, val)

    def modify(self, tte):
        if self.Value:
            return 0
        else:
            return tte

    def update(self, value, **kwargs):
        val = bool(value)
        if self.Value ^ val:
            self.Value = val
            return True
        else:
            return False

    def clone(self):
        return BuffModifier(self.Target, self.Value)


class ModifierSet:
    def __init__(self):
        self.Mods = OrderedDict()

    def __setitem__(self, name, mod):
        self.Mods[name] = mod

    def __getitem__(self, name):
        return self.Mods[name]

    def on(self, tr):
        return [mod for mod in self.Mods.values() if mod.Target == tr]

    def __repr__(self):
        return ', '.join(['{}={}'.format(k, v.Value) for k, v in self.Mods.items()])

    def __str__(self):
        return ', '.join([v.Value for v in self.Mods.values()])

    def to_json(self):
        return {k: v.Value for k, v in self.Mods.items()}
