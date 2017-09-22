import re
import numpy as np
__author__ = 'TimeWz667'
__all__ = ['ModelSelector']


Pats = {
    'PC': (r'PC\s*=\s*(\w+)', lambda x, v: x.Meta.PC == v),
    'DC': (r'DC\s*=\s*(\w+)', lambda x, v: x.Meta.DC == v),
    'MC': (r'MC\s*=\s*(\w+)', lambda x, v: x.Meta.Prototype == v),
    'Proto': (r'\.(\w+)', lambda x, v: x.Meta.Prototype == v),
    'Prefix': (r'#(\w+)', lambda x, v: x.Name.find(v) == 0),
    'Name': (r'(\w+)', lambda x, v: x.Name == v)
}


class ModelSelector:
    def __init__(self, models):
        self.Models = models

    def select_all(self, sel):
        ss, _ = ModelSelector.parse_selector(sel)
        if not ss:
            return self
        mods = self.Models
        for selector in ss:
            mods = {k: mod for k, mod in mods.items() if selector[0](mod, selector[1])}
        return ModelSelector(mods)

    def __iter__(self):
        return iter(self.Models)

    def keys(self):
        return self.Models.keys()

    def values(self):
        return self.Models.values()

    def items(self):
        return self.Models.items()

    def first(self):
        for v in self.Models.values():
            return v

    def sum_up(self, sel, par):
        ss, sp = ModelSelector.parse_selector(sel)
        if not ss:
            return self
        mods = self.Models
        for selector in ss:
            mods = [mod for mod in mods if selector[0](mod, selector[1])]
        vs = list()
        for mod in mods:
            try:
                vs.append(mod[par])
            except KeyError:
                continue

        par = par if sp is '*' else '{}({})'.format(par, sp)

        return par, np.array(vs).sum()

    def foreach(self, fn):
        for mod in self.Models:
            fn(mod)

    def map(self, fn):
        return [fn(mod) for mod in self.Models]

    def reduce(self, fn, ini=0):
        val = ini
        for mod in self.Models:
            val = fn(val, mod)
        return val

    def extract(self, k):
        vs = list()
        for mod in self.Models.values():
            try:
                vs.append(mod[k])
            except KeyError:
                continue
        return np.array(vs)

    def __repr__(self):
        return ', '.join([mod.Name for mod in self.Models])

    @staticmethod
    def parse_selector(sel):
        ss = list()
        if sel.find('*') >= 0:
            return ss, '*'
        sp = list()
        for reg, fil in Pats.values():
            sr = re.search(reg, sel, re.I)
            if sr:
                ss.append((fil, sr.group(1)))
                sp.append(sr.group(0))
        if not ss:
            raise ValueError('No matched pattern')
        sp = ','.join(sp)
        sp = sp.replace(' ', '')
        return ss, sp


if __name__ == '__main__':
    ss1, sp1 = ModelSelector.parse_selector('PC  =A , #B, .C')

    print(sp1)
    for s in ss1:
        print(s)
