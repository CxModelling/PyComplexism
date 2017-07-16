from collections import namedtuple
import re
from .modelset import ModelSet


__author__ = 'TimeWz667'


SingleEntry = namedtuple('SingleEntry', ('Name', 'Prototype', 'Y0'))
MultipleEntry = namedtuple('MultipleEntry', ('Name', 'Prototype', 'Y0', 'Index'))


class RelationEntry:
    def __init__(self, val, parse=True):
        self.Model, self.Type, self.Parameter = RelationEntry.parse(val) if parse else val

    def __repr__(self):
        return 'Model: {}, Type: {}, Parameter: {}'.format(self.Model, self.Type, self.Parameter)

    def is_single(self):
        return self.Type == 'Name'

    def to_json(self):
        return {
            'Model': self.Model,
            'Type': self.Type,
            'Parameter': self.Parameter
        }

    @staticmethod
    def from_json(js):
        ent = js['Model'], js['Type'], js['Parameter']
        return RelationEntry(ent, parse=False)

    @staticmethod
    def parse(s):
        s = re.search(r'((?P<x>\w+)|(#(?P<y>\w+))|(.(?P<z>\w+))\s*)@(?P<par>\w+)', s)
        if not s.group('par'):
            raise ValueError('Undefined parameter')
        if s.group('y'):
            return s.group('y'), 'Prefix', s.group('par')
        elif s.group('z'):
            return s.group('z'),'Prototype',  s.group('par')
        elif s.group('x'):
            return s.group('x'), 'Name', s.group('par')
        else:
            raise ValueError('Undefined model description')


class ModelLayout:
    def __init__(self, name):
        self.Name = name
        self.Entries = list()
        self.Relations = list()
        self.Summary = list()
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
            self.Relations.append({'Source': RelationEntry(source), 'Target': RelationEntry(target)})
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

    def find_model_by_prototype(self, proto):
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
            src, tar = rel['Source'], rel['Target']
            tp = tar.Parameter

            if tar.Type == 'Name':
                tar = [tar.Model]
            elif tar.Type == 'Prefix':
                tar = self.find_model_by_prefix(tar.Model)
            elif tar.Type == 'Prototype':
                tar = self.find_model_by_prototype(tar.Model)

            yield src, tp, tar

    def count_prototype(self):
        proto = [ent.Prototype for ent in self.Entries]
        proto = set(proto)
        return len(proto)

    def generate(self, gen, reduce=False, dt_update=1):
        # todo
        if dt_update <=0:
            return None

        if len(self.Entries) is 1 & isinstance(self.Entries[0], SingleEntry):
            name, proto, y0 = self.Entries[0]
            return gen(proto, name), y0

        models = None
        if reduce:
            # todo select best structure
            pass
        else:
            models = ModelSet(self.Name, dt_update)
            y0s = dict()

            for mod in self.models():
                name, proto, y0 = mod
                models.append(gen(proto, name))
                y0s[name] = y0

        for rel in self.Relations:
            pass

        return models, y0s

    def to_json(self):
        # todo
        pass

    @staticmethod
    def from_json(js):
        # todo
        pass


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
