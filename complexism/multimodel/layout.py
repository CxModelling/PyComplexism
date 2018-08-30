from complexism.mcore import BranchY0
from complexism.multimodel.mm import MultiModel
from complexism.multimodel.entries import *

__author__ = 'TimeWz667'


class ModelLayout:
    def __init__(self, name):
        self.Name = name
        self.Entries = list()
        self.Interactions = list()
        self.Actors = list()
        self.Children = dict()
        self.ObsChildren = []
        self.ObsActors = []

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

    def add_interaction(self, selector, checker, response):
        self.Interactions.append(InteractionEntry(selector, checker, response))

    def add_interaction_js(self, js):
        self.Interactions.append((InteractionEntry.from_json(js)))

    def set_observations(self, children=None, actors=None):
        if children:
            if isinstance(children, str):
                self.ObsChildren.append(children)
            else:
                self.ObsChildren = list(children)

        if actors:
            if isinstance(children, str):
                self.ObsActors.append(children)
            else:
                self.ObsActors = list(children)

    def models(self):
        for v in self.Entries:
            for m in v.gen():
                yield m

    def count_prototype(self):
        proto = [ent.Prototype for ent in self.Entries]
        proto = set(proto)
        return len(proto)

    def get_parameter_hierarchy(self, da):
        hie = {}
        chd = []
        for ent in self.Entries:
            if ent not in hie:
                pro = ent.Prototype
                hie.update(da.get_sim_model(pro).get_parameter_hierarchy(da))
                chd.append(pro)

        for sub in self.Children:
            if sub.Name not in hie:
                hie[sub.Name] = sub.get_parameter_hierarchy(da)
                chd.append(sub.Name)

        hie[self.Name] = chd
        return hie

    def generate(self, name, da, pc, all_obs=False):
        models = MultiModel(name, pars=pc)

        for mod in self.models():
            name, proto, _ = mod
            sub_pc = pc.breed(name, proto)
            m = da.generate_mc(name, proto, pc=sub_pc, da=da)
            models.append_child(m, all_obs or proto in self.ObsChildren)

        for interaction in self.Interactions:
            for m in models.select_all(interaction.Selector).values():
                m.add_listener(interaction.pass_checker(), interaction.pass_response())

        for act in self.ObsActors:
            models.add_observing_actor(act)

        return models

    def get_y0s(self):
        y0s = BranchY0()
        for mod in self.models():
            name, _, y0 = mod
            y0s.append_child(name, y0)
        return y0s

    def to_json(self):
        js = dict()
        js['Name'] = self.Name
        js['Entries'] = [ent.to_json() for ent in self.Entries]
        js['Interactions'] = [inter.to_json() for inter in self.Interactions]
        return js

    @staticmethod
    def from_json(js):
        lyo = ModelLayout(js['Name'])
        for ent in js['Entries']:
            if 'Index' in ent:
                lyo.add_entry(ent['Name'], ent['Prototype'], ent['Y0'], **ent['Index'])
            else:
                lyo.add_entry(ent['Name'], ent['Prototype'], ent['Y0'])

        for inter in js['Interactions']:
            lyo.add_interaction_js(inter)
        return lyo


if __name__ == '__main__':
    lm1 = ModelLayout('')
    lm1.add_entry('A', 'm1', 1)
    lm1.add_entry('B', 'm2', 2, size=2)
    lm1.add_entry('B', 'm2', 3, size=2, fr=2)
    lm1.add_entry('C', 'm2', 3, size=2)
    for mo in lm1.models():
        print(mo)

    print(lm1.count_prototype())

    jsm = lm1.to_json()
    print(jsm)

    lm2 = ModelLayout.from_json(jsm)
    print(lm2.to_json())
