from abc import abstractmethod, ABCMeta
from collections import OrderedDict

__author__ = 'TimeWz667'


class AbsModifier(metaclass=ABCMeta):
    def __init__(self, name, tar):
        self.Name = name
        self.__Target = tar

    @property
    @abstractmethod
    def value(self):
        pass

    @property
    def target(self):
        return self.__Target

    @abstractmethod
    def modify(self, tte, ti=0):
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    def __repr__(self):
        return 'Mod {} on {}'.format(self.Name, self.__Target.Name)

    @abstractmethod
    def clone(self):
        pass


class DirectModifier(AbsModifier):

    def __init__(self, name, tar):
        AbsModifier.__init__(self, name, tar)
        self.Val = float('inf')

    @property
    def value(self):
        return self.Val

    def modify(self, tte, ti=0):
        if self.Val <= 0:
            return float('inf')

        return self.Val

    def update(self, val):
        if self.Val is not val:
            self.Val = val
            return True
        else:
            return False

    def clone(self):
        return DirectModifier(self.Name, self.target)


class LocRateModifier(AbsModifier):

    def __init__(self, name, tar):
        AbsModifier.__init__(self, name, tar)
        self.Val = 0

    @property
    def value(self):
        return self.Val

    def modify(self, tte, ti=0):
        if self.Val <= 0:
            return float('inf')

        return tte/self.Val

    def update(self, val):
        if self.Val is not val:
            self.Val = val
            return True
        else:
            return False

    def clone(self):
        return LocRateModifier(self.Name, self.target)


class GloRateModifier(AbsModifier):
    def __init__(self, name, tar):
        AbsModifier.__init__(self, name, tar)
        self.Val = 0

    @property
    def value(self):
        return self.Val

    def modify(self, tte, ti=0):
        if self.Val <= 0:
            return float('inf')

        return tte/self.Val

    def update(self, val):
        if self.Val is not val:
            self.Val = val
            return True
        else:
            return False

    def clone(self):
        return self


class NerfModifier(AbsModifier):
    def __init__(self, name, tar):
        AbsModifier.__init__(self, name, tar)
        self.Val = False

    @property
    def value(self):
        return self.Val

    def modify(self, tte, ti=0):
        if self.Val:
            return float('inf')
        else:
            return tte

    def update(self, val):
        if self.Val is not val:
            self.Val = val
            return True
        else:
            return False

    def clone(self):
        return self


class BuffModifier(AbsModifier):
    def __init__(self, name, tar):
        AbsModifier.__init__(self, name, tar)
        self.Val = False

    @property
    def value(self):
        return self.Val

    def modify(self, tte, ti=0):
        if self.Val:
            return 0
        else:
            return tte

    def update(self, val):
        if self.Val is not val:
            self.Val = bool(val)
            return True
        else:
            return False

    def clone(self):
        return self


class ModifierSet:
    def __init__(self):
        self.Mods = OrderedDict()

    def __setitem__(self, name, mod):
        self.Mods[name] = mod

    def __getitem__(self, name):
        return self.Mods[name]

    def on(self, tr):
        return [mod for mod in self.Mods.values() if mod.target == tr]

    def __repr__(self):
        return ', '.join(['{}={}'.format(k, v.value) for k, v in self.Mods.items()])

    def __str__(self):
        return ', '.join([v.value for v in self.Mods.values()])

    def to_json(self):
        return {k: v.value for k, v in self.Mods.items()}
