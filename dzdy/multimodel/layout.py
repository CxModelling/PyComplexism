from dzdy.multimodel.modelset import ModelSet
from dzdy.multimodel.entries import *

__author__ = 'TimeWz667'


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

    def add_relation(self, source, target, js=False):
        try:
            if js:
                self.Relations.append({'Source': RelationEntry.from_json(source),
                                       'Target': RelationEntry.from_json(target)})
            else:
                self.Relations.append({'Source': RelationEntry(source),
                                       'Target': RelationEntry(target)})
        except ValueError as e:
            raise e

    def set_observations(self, mods):
        self.Summary += mods

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

    def generate(self, gen, odt=0.5):
        if odt <= 0:
            return None

        if len(self.Entries) is 1 & isinstance(self.Entries[0], SingleEntry):
            name, proto, y0 = self.Entries[0]
            return gen(proto, name), y0

        models = ModelSet(self.Name, odt)
        y0s = dict()

        for mod in self.models():
            name, proto, y0 = mod
            models.append(gen(proto, name))
            y0s[name] = y0

        for rel in self.Relations:
            models.link(rel['Source'], rel['Target'])

        for mod in self.Summary:
            models.add_obs_model(mod)

        return models, y0s

    def to_json(self):
        js = dict()
        js['Name'] = self.Name
        js['Entries'] = [ent.to_json() for ent in self.Entries]
        js['Relations'] = [{'Source': rel['Source'].to_json(), 'Target': rel['Target'].to_json()}
                           for rel in self.Relations]
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
            lyo.add_relation(rel['Source'], rel['Target'], js=True)
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
