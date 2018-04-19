import numpy.random as rd
from epidag import parse_distribution
from complexism.util import CategoricalRV
from abc import ABCMeta, abstractmethod

__author__ = 'TimeWz667'
__all__ = ['TraitSet', 'TraitBinary', 'TraitDistribution', 'TraitCategory',
           'AbsTrait']


class TraitSet:
    def __init__(self):
        self.Traits = list()

    def append(self, f):
        if callable(f):
            self.Traits.append(f)

    def __call__(self, info=None):
        info = info if info else {}
        for f in self.Traits:
            info = f(info)
        return info

    def to_json(self):
        return [js.to_json() for js in self.Traits]

    def __str__(self):
        return str(self.to_json())

    def list(self):
        return [trt.Name for trt in self.Traits]


class AbsTrait(metaclass=ABCMeta):
    @abstractmethod
    def to_json(self):
        pass

    def __repr__(self):
        return str(self.to_json())


class TraitBinary(AbsTrait):
    def __init__(self, name, prob, tf=(1, 0)):
        self.Name = name
        self.Prob = prob
        self.TrueFalse = tf

    def __call__(self, info):
        if self.Name in info:
            return info
        info[self.Name] = \
            self.TrueFalse[0] if rd.random() < self.Prob else self.TrueFalse[1]
        return info

    def to_json(self):
        return {'Name': self.Name, 'Type': 'Binary',
                'prob': self.Prob, 'tf': [self.TrueFalse[0], self.TrueFalse[1]]}


class TraitDistribution(AbsTrait):
    def __init__(self, name, dist):
        self.Name = name
        self.Dist = parse_distribution(dist)

    def __call__(self, info):
        if self.Name in info:
            return info
        info[self.Name] = self.Dist.sample()
        return info

    def to_json(self):
        return {'Name': self.Name, 'Type': 'Distribution',
                'dist': self.Dist.Name}


class TraitCategory(AbsTrait):
    def __init__(self, name, kv):
        self.Name = name
        self.Cat = CategoricalRV(kv)

    def __call__(self, info):
        if self.Name in info:
            return info
        info[self.Name] = self.Cat.rvs()
        return info

    def to_json(self):
        return {'Name': self.Name, 'Type': 'Category',
                'kv': self.Cat.get_xs()}


if __name__ == '__main__':
    fs_test = TraitSet()
    fs_test.append(TraitBinary('Sex', 0.5, ['M', 'F']))
    fs_test.append(TraitDistribution('Height', 'norm(170, 10)'))
    fs_test.append(TraitCategory('Area', {'A': 1, 'B': 2, 'C': 3}))
    print(fs_test)
    print(fs_test({}))
    print(fs_test({}))

    fs_js = fs_test.to_json()

    print(fs_test)
