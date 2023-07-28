from abc import ABCMeta, abstractmethod

__all__ = ['AbsY0', 'LeafY0', 'BranchY0']


class AbsY0(metaclass=ABCMeta):
    def __init__(self):
        self.Entries = list()

    @abstractmethod
    def match_model_info(self, model):
        pass

    def define(self, **kwargs):
        self.Entries.append(kwargs)

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

    @staticmethod
    @abstractmethod
    def from_prototype(proto):
        pass

    @abstractmethod
    def clone(self):
        pass

    def print(self):
        # todo recode
        if self.Entries:
            print(type(self).__name__ + ' Entries: ')
            for ent in self.Entries:
                print('\t' + str(ent))
        else:
            print(type(self).__name__ + ' Empty Y0')


class LeafY0(AbsY0):
    def __init__(self):
        AbsY0.__init__(self)

    def match_model_info(self, model):
        pass

    def define(self, **kwargs):
        self.Entries.append(kwargs)

    def to_json(self):
        js = AbsY0.to_json(self)
        js['Type'] = 'Leaf'
        return js

    def clone(self):
        return LeafY0.from_json(self.to_json())

    @staticmethod
    def from_source(src):
        assert isinstance(src, list)
        y0 = LeafY0()
        for ent in src:
            y0.define(**ent)
        return y0

    @staticmethod
    def from_json(js):
        assert isinstance(js, dict)
        assert 'Entries' in js
        return LeafY0.from_source(js['Entries'])

    @staticmethod
    def from_prototype(proto):
        assert issubclass(type(proto), LeafY0)
        return proto


class BranchY0(AbsY0):
    def __init__(self):
        AbsY0.__init__(self)
        self.ChildrenY0 = dict()

    def __getitem__(self, item):
        return self.ChildrenY0[item]

    def append_child(self, key, chd):
        if not issubclass(type(chd), AbsY0):
            if isinstance(chd, list):
                chd = LeafY0.from_source(chd)
            elif isinstance(chd, dict):
                if chd['Type'] == 'Leaf':
                    chd = LeafY0.from_json(chd)
                else:
                    chd = BranchY0.from_json(chd)
            else:
                raise TypeError('Unknown type of children')
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
        return BranchY0.from_json(self.to_json())

    @staticmethod
    def from_source(src):
        assert isinstance(src, list)
        y0 = LeafY0()
        for ent in src:
            y0.define(**ent)
        return y0

    @staticmethod
    def from_json(js):
        y0s = BranchY0()
        for k, v in js['Children'].items():
            y0s.append_child(k, v)
        for ent in js['Entries']:
            y0s.define(**ent)
        return y0s

    @staticmethod
    def from_prototype(proto):
        assert issubclass(type(proto), BranchY0)
        return proto

    def print(self):
        AbsY0.print(self)
        for k, v in self.ChildrenY0.items():
            print('|- {} -|'.format(k))
            v.print()
