import re
from dzdy.multimodel.modelset import ModelSet


__author__ = 'TimeWz667'


class SingleEntry:
    def __init__(self, name, proto, y0):
        self.Name = name
        self.Prototype = proto
        self.Y0 = y0

    def __repr__(self):
        return 'Model: {}, Prototype: {}'.format(self.Name, self.Prototype)

    def gen(self):
        yield self.Name, self.Prototype, self.Y0

    def to_json(self):
        return {
            'Name': self.Name,
            'Prototype': self.Prototype,
            'Y0': self.Y0
        }

    @staticmethod
    def from_json(js):
        ent = js['Name'], js['Prototype'], js['Y0']
        return SingleEntry(*ent)


class MultipleEntry:
    def __init__(self, name, proto, y0, index):
        self.Name = name
        self.Prototype = proto
        self.Y0 = y0
        self.Index = index

    def __repr__(self):
        return 'Model: {}, Prototype: {}'.format(self.Name, self.Prototype)

    def gen(self):
        if 'index' in self.Index:
            index = self.Index['index']
        elif 'size' in self.Index:
            if 'fr' in self.Index:
                index = range(self.Index['fr'], self.Index['size']+self.Index['fr'])
            else:
                index = range(self.Index['size'])
        elif 'fr' in self.Index and 'to' in self.Index:
            if 'by' in self.Index:
                index = range(self.Index['fr'], self.Index['to'] + 1, step=self.Index['by'])
            else:
                index = range(self.Index['fr'], self.Index['to'] + 1)
        else:
            raise IndexError('No matched index pattern')

        for i in index:
            yield '{}_{}'.format(self.Name, i), self.Prototype, self.Y0

    def to_json(self):
        return {
            'Name': self.Name,
            'Prototype': self.Prototype,
            'Y0': self.Y0,
            'Index': self.Index
        }

    @staticmethod
    def from_json(js):
        ent = js['Name'], js['Prototype'], js['Y0'], js['Index']
        return MultipleEntry(*ent)


class RelationEntry:
    def __init__(self, val, parse=True):
        self.Selector, self.Type, self.Parameter = RelationEntry.parse(val) if parse else val

    def __repr__(self):
        return 'Selector: {}, Type: {}, Parameter: {}'.format(self.Selector, self.Type, self.Parameter)

    def is_single(self):
        return self.Type == 'Single'

    def to_json(self):
        return {
            'Selector': self.Selector,
            'Type': self.Type,
            'Parameter': self.Parameter
        }

    @staticmethod
    def from_json(js):
        ent = js['Selector'], js['Type'], js['Parameter']
        return RelationEntry(ent, parse=False)

    @staticmethod
    def parse(ori):
        s = re.match('\A\w+\Z', ori)
        par = re.search('@(\w+\Z)', 'Abd @P1')

        if not par:
            raise ValueError('Undefined parameter')
        if s:
            return ori, 'Single', par.group(1)
        else:
            return ori, 'Multiple', par.group(1)


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
            index = {'size': kwargs['size']}
            if 'fr' in kwargs:
                index['fr'] = kwargs['fr']
        elif 'fr' in kwargs and 'to' in kwargs:
            index = {'fr': kwargs['fr'], 'to': kwargs['to']}
            if 'by' in kwargs:
                index['by'] = kwargs['by']

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
            for m in v.gen():
                yield m

    def relations(self):
        for rel in self.Relations:
            src, tar = rel['Source'], rel['Target']
            yield src, tar

    def count_prototype(self):
        proto = [ent.Prototype for ent in self.Entries]
        proto = set(proto)
        return len(proto)

    def generate(self, gen, reduce=False, dt_update=1):
        if dt_update <= 0:
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
        js = dict()
        js['Name'] = self.Name
        js['Entries'] = [ent.to_json() for ent in self.Entries]
        js['Relations'] = [{'Source': rel['Source'].to_json(), 'Target': rel['Target'].to_json()} for rel in self.Relations]
        return js

    @staticmethod
    def from_json(js):
        lyo = ModelLayout(js['Name'])
        for ent in js['Entries']:
            if 'Index' in ent:
                lyo.add_entry(ent['Name'], ent['Prototype'], ent['Y0'], **ent['Index'])
            else:
                lyo.add_entry(ent['Name'], ent['Prototype'], ent['Y0'])

        for rel in js['Relations']:
            lyo.add_relation(rel['Source']['Selector'], rel['Target']['Selector'])
        return lyo


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

    jsm = lm1.to_json()
    print(jsm)

    lm2 = ModelLayout.from_json(jsm)
    print(lm2.to_json())
