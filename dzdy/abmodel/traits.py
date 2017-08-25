import numpy.random as rd
from epidag import parse_distribution
from dzdy.util import CategoricalRV
import dzdy.validators as vld
from abc import ABCMeta, abstractmethod, abstractstaticmethod

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

    @staticmethod
    def from_json(js):
        ts = TraitSet()
        for fn in js:
            ts.append(get_trait(fn))
        return ts


class AbsTrait(metaclass=ABCMeta):
    @abstractmethod
    def to_json(self):
        pass

    @abstractstaticmethod
    def from_json(js):
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
                'Prob': self.Prob, 'TF': [self.TrueFalse[0], self.TrueFalse[1]]}

    @staticmethod
    def from_json(js):
        return TraitBinary(js['Name'], js['Prob'], js['TF'])

    @staticmethod
    def get_validators(**kwargs):
        return {'Prob': vld.Number(lower=0, upper=1), 'TF': vld.ListSize(2)}

    @staticmethod
    def get_template(i=0):
        return {'Name': 'Is_{}'.format(i), 'Type': 'Binary', 'Prob': 0.5, 'TF': [1, 0]}


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
                'Distribution': self.Dist.Name}

    @staticmethod
    def from_json(js):
        return TraitDistribution(js['Name'], js['Distribution'])

    @staticmethod
    def get_validators(**kwargs):
        # todo validator for distributions
        return {}

    @staticmethod
    def get_template(i=0):
        return {'Name': 'Is_{}'.format(i), 'Type': 'Distribution', 'Distribution': 'exp(1.0)'}


class TraitCategory(AbsTrait):
    def __init__(self, name, xs):
        self.Name = name
        self.Cat = CategoricalRV(xs)

    def __call__(self, info):
        if self.Name in info:
            return info
        info[self.Name] = self.Cat.rvs()
        return info

    def to_json(self):
        return {'Name': self.Name, 'Type': 'Category',
                'KV': self.Cat.get_xs()}

    @staticmethod
    def from_json(js):
        return TraitCategory(js['Name'], js['KV'])

    @staticmethod
    def get_validators(**kwargs):
        return {'KV': vld.ProbTab()}

    @staticmethod
    def get_template(i=0):
        return {'Name': 'Is_{}'.format(i), 'Type': 'Category', 'KV': {'A': 0.5, 'B': 0.5}}




if __name__ == '__main__':
    fs_test = TraitSet()
    fs_test.append(TraitBinary('Sex', 0.5, ['M', 'F']))
    fs_test.append(TraitDistribution('Height', 'norm(170, 10)'))
    fs_test.append(TraitCategory('Area', {'A': 1, 'B': 2, 'C': 3}))
    print(fs_test)
    print(fs_test({}))
    print(fs_test({}))

    fs_js = fs_test.to_json()
    for j in fs_js:
        print(get_trait(j))
    fs_test = TraitSet.from_json(fs_js)
    print(fs_test)
