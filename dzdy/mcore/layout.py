from collections import namedtuple, OrderedDict
import re

__author__ = 'TimeWz667'


SingleEntry = namedtuple('SingleEntry', ('Name', 'Prototype', 'Y0'))
MultipleEntry = namedtuple('MultipleEntry', ('Name', 'Prototype', 'Y0', 'Index'))


class ModelRelation:
    def __init__(self, src, tar, parse=True):
        self.SRC = ModelRelation.parse(src) if parse else src
        self.TAR = ModelRelation.parse(tar) if parse else tar

    def __repr__(self):
        return 'Src: {}, Target: {}'.format(self.SRC, self.TAR)

    def to_json(self):
        return {
            'Src': list(self.SRC),
            'Tar': list(self.TAR)
        }

    @staticmethod
    def from_json(js):
        return ModelRelation(js['Src'], js['Tar'], False)

    @staticmethod
    def parse(s):
        s = re.search(r'((?P<x>\w+)|(#(?P<y>\w+))|(.(?P<z>\w+))\s*)@(?P<par>\w+)', s)
        if not s.group('par'):
            raise ValueError('Undefined parameter')
        if s.group('y'):
            return 'Prefix', s.group('y'), s.group('par')
        elif s.group('z'):
            return 'Proto', s.group('z'), s.group('par')
        elif s.group('x'):
            return 'Name', s.group('x'), s.group('par')
        else:
            raise ValueError('Undefined model description')


class ModelLayout:
    def __init__(self, name):
        self.Name = name
        self.Entries = list()
        self.Relations = list()
        self.Children = dict()

    def append_child(self, chd):
        self.Children[chd.Name] = chd

    def add_entry(self, name, proto, y0, **kwargs):
        index = None
        if 'index' in kwargs:
            index = kwargs['index']
        elif 'size' in kwargs:
            if 'fr' in kwargs:
                index = range(kwargs['fr'], kwargs['size']+kwargs['fr'])
            else:
                index = range(kwargs['size'])
        elif 'fr' in kwargs and 'to' in kwargs:
            if 'by' in kwargs:
                index = range(kwargs['fr'], kwargs['to'] + 1, step=kwargs['by'])
            else:
                index = range(kwargs['fr'], kwargs['to'] + 1)

        if index:
            self.Entries.append(MultipleEntry(name, proto, y0, index))
        else:
            self.Entries.append(SingleEntry(name, proto, y0))

    def add_relation(self, source, target):
        try:
            self.Relations.append(ModelRelation(source, target))
        except ValueError as e:
            raise e

    def models(self):
        for v in self.Entries:
            if isinstance(v, MultipleEntry):
                for i in v.Index:
                    yield '{}_{}'.format(v.Name, i), v.Prototype, v.Y0
            else:
                yield v

    def find_model_by_prefix(self, prefix):
        ms = list()
        for v in self.Entries:
            if isinstance(v, MultipleEntry) and v.Name == prefix:
                for i in v.Index:
                    ms.append('{}_{}'.format(v.Name, i))

        return ms

    def find_model_by_proto(self, proto):
        ms = list()
        for v in self.Entries:
            if v.Prototype == proto:
                if isinstance(v, MultipleEntry):
                    for i in v.Index:
                        ms.append('{}_{}'.format(v.Name, i))
                else:
                    ms.append(v.Name)
        return ms

    def relations(self):
        for rel in self.Relations:
            src, tar = rel.SRC, rel.TAR
            sp, tp = None, None
            if src[0] == 'Name':
                src, sp = [src[1]], src[2]
            elif src[0] == 'Prefix':
                src, sp = self.find_model_by_prefix(src[1]), src[2]
            elif src[0] == 'Proto':
                src, sp = self.find_model_by_proto(src[1]), src[2]

            if tar[0] == 'Name':
                tar, tp = [tar[1]], tar[2]
            elif tar[0] == 'Prefix':
                tar, tp = self.find_model_by_prefix(tar[1]), tar[2]
            elif tar[0] == 'Proto':
                tar, tp = self.find_model_by_proto(tar[1]), tar[2]

            for s in src:
                for t in tar:
                    if s != t:
                        yield s, sp, t, tp

    def count_prototype(self):
        proto = [ent.Prototype for ent in self.Entries]
        proto = set(proto)
        return len(proto)

if __name__ == '__main__':
    lm1 = ModelLayout('')
    lm1.add_entry('A', 'm1', 1)
    lm1.add_entry('B', 'm2', 2, size=2)
    lm1.add_entry('B', 'm2', 3, size=2, fr=2)
    lm1.add_entry('C', 'm2', 3, size=2)
    for mo in lm1.models():
        print(mo)

    print('\nRelations:')

    lm1.add_relation('B_1@P1', '#B@P2')
    lm1.add_relation('#C@P3', '.m2@P4')

    for r in lm1.relations():
        print(r)

    print(lm1.count_prototype())
