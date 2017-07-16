import re
__author__ = 'TimeWz667'
__all__ = ['ModelSelector']


Pats = {
    'PC': (r'PC\s*=\s*(\w+)', lambda x, v: x.Meta.PC == v),
    'DC': (r'DC\s*=\s*(\w+)', lambda x, v: x.Meta.DC == v),
    'MC': (r'MC\s*=\s*(\w+)', lambda x, v: x.Meta.Prototype == v),
    'Proto': (r'#(\w+)', lambda x, v: x.Meta.Prototype == v),
    'Prefix': (r'\.(\w+)', lambda x, v: x.Name.find(v) == 0)
}


class ModelSelector:
    def __init__(self, models):
        self.Models = models

    def select_all(self, sel):
        ss = ModelSelector.parse_selector(sel)
        if not ss:
            return ModelSelector(list())
        mods = self.Models
        for selector in ss:
            mods = [mod for mod in mods if selector[0](mod, selector[1])]
        return ModelSelector(mods)

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

    def __repr__(self):
        return ', '.join([mod.Name for mod in self.Models])

    @staticmethod
    def parse_selector(sel):
        ss = list()
        for reg, fil in Pats.values():
            sr = re.search(reg, sel, re.I)
            if sr:
                ss.append((fil, sr.group(1)))
        return ss


if __name__ == '__main__':
    for s in ModelSelector.parse_selector('PC=A, #B, .C'):
        print(s)
