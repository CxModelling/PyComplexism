from abc import ABCMeta, abstractmethod

__all__ = ['LeafY0', 'BranchY0']


class AbsY0(metaclass=ABCMeta):
    def __init__(self, src=None):
        if not src:
            self.Entries = list()
        elif isinstance(src, list):
            self.Entries = [ent for ent in src]
        elif isinstance(src, dict):
            self.Entries = [ent for ent in src['Entries']]
        else:
            raise TypeError('Known source type')

    @abstractmethod
    def match_model_info(self, model):
        pass

    @abstractmethod
    def define(self, entry, **kwargs):
        pass

    def __iter__(self):
        return iter(self.Entries)

    @abstractmethod
    def to_json(self):
        js = {'Entries': list(self.Entries)}
        return js

    @staticmethod
    @abstractmethod
    def from_source(src):
        pass

    @staticmethod
    @abstractmethod
    def from_json(js):
        pass

    @abstractmethod
    def clone(self):
        pass


class LeafY0(AbsY0):
    def __init__(self, src=None):
        AbsY0.__init__(self, src)

    def match_model_info(self, model):
        pass

    def define(self, ent, **kwargs):
        self.Entries.append(ent)

    def to_json(self):
        js = AbsY0.to_json(self)
        js['Type'] = 'Leaf'
        return js

    def clone(self):
        return LeafY0(self.to_json())

    @staticmethod
    def from_source(src):
        return LeafY0(src)

    @staticmethod
    def from_json(js):
        return LeafY0(js)


class BranchY0(AbsY0):
    def __init__(self, src=None, chd=None):
        AbsY0.__init__(self, src)

        if isinstance(src, dict):
            chd = src['Children']
            self.ChildrenY0 = dict(chd) if chd else dict()
        elif isinstance(chd, dict):
            self.ChildrenY0 = dict(chd)
        else:
            self.ChildrenY0 = dict()

    def __getitem__(self, item):
        return self.ChildrenY0[item]

    def append_child(self, key, chd):
        self.ChildrenY0[key] = chd

    def match_model_info(self, model):
        pass

    def define(self, ent, **kwargs):
        self.Entries.append(ent)

    def to_json(self):
        js = AbsY0.to_json(self)
        js['Type'] = 'Branch'
        js['Children'] = {k: v.to_json() for k, v in self.ChildrenY0.items()}
        return js

    def clone(self):
        return BranchY0(self.to_json())

    @staticmethod
    def from_source(src):
        y0s = BranchY0()
        for k, v in src['Children'].items():
            y0s.append_child(k, LeafY0.from_json(v))
        return y0s

    @staticmethod
    def from_json(js):
        return BranchY0(js)
