import numpy.random as rd
from pcore import parse_distribution
import json
from dzdy.util import CategoricalRV

__author__ = 'TimeWz667'


class FillUpSet:
    def __init__(self):
        self.FillUps = list()

    def append(self, f):
        if callable(f):
            self.FillUps.append(f)

    def __call__(self, info=None):
        info = info if info else {}
        for f in self.FillUps:
            info = f(info)
        return info

    def append_json(self, js):
        if isinstance(js, str):
            js = json.loads(js)
        try:
            if js['Type'] == 'Binary':
                self.append(FillBinary(js['Name'], js['Prob'], js['TF']))
            elif js['Type'] == 'Distribution':
                self.append(FillDistribution(js['Name'], js['Distribution']))
            elif js['Type'] == 'Category':
                self.append(FillCategory(js['Name'], js['KV']))
        except KeyError:
            print('Pool-defined function')
            return

    def to_json(self):
        return [js.to_json() for js in self.FillUps]

    def __str__(self):
        return str(self.to_json())


class FillBinary:
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


class FillDistribution:
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


class FillCategory:
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


if __name__ == '__main__':
    fs_test = FillUpSet()
    fs_test.append(FillBinary('Sex', 0.5, ['M', 'F']))
    fs_test.append(FillDistribution('Height', 'norm(170, 10)'))
    fs_test.append(FillCategory('Area', {'A': 1, 'B': 2, 'C': 3}))
    print(fs_test)
    print(fs_test({}))
    print(fs_test({}))

    fs_js = fs_test.to_json()
    fs_test = FillUpSet()
    for j in fs_js:
        fs_test.append_json(json.dumps(j))
    print(fs_test)
