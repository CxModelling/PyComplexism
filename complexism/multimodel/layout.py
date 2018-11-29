import epidag as dag
from complexism.mcore import BranchY0, AbsModelBlueprint
from complexism.multimodel.mm import MultiModel
from complexism.multimodel.entries import *

__author__ = 'TimeWz667'


class ModelLayout(AbsModelBlueprint):
    def __init__(self, name):
        AbsModelBlueprint.__init__(self, name)
        self.Entries = list()
        self.Interactions = list()
        self.Actors = list()
        self.ObsActors = []
        self.ObsModels = []
        self.Summaries = dict()
        self.ObsAllModels = False

    def add_entry(self, name, proto, y0=None, **kwargs):
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

    def add_entry_js(self, js):
        if 'Index' in js:
            self.Entries.append(MultipleEntry.from_json(js))
        else:
            self.Entries.append(SingleEntry.from_json(js))

    def add_interaction(self, selector, checker, response):
        self.Interactions.append(InteractionEntry(selector, checker, response))

    def add_interaction_js(self, js):
        self.Interactions.append((InteractionEntry.from_json(js)))

    def set_observations(self, models=None, actors=None):
        if models:
            if isinstance(models, str):
                self.ObsModels.append(models)
            else:
                self.ObsModels = list(models)

        if actors:
            if isinstance(actors, str):
                self.ObsActors.append(actors)
            else:
                self.ObsActors = list(actors)

        if not models and not actors:
            self.ObsAllModels = True

    def add_summary(self, selector, key, new_name=None):
        if not new_name:
            new_name = '{}_{}'.format(selector, key)
        if new_name not in self.Summaries:
            self.Summaries[new_name] = SummaryEntry(selector, key, new_name)

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
                m = da.get_sim_model(pro)
                hie.update(m.get_parameter_hierarchy(da))
                chd.append(pro)

        hie[self.Class] = chd
        return hie

    def generate(self, name, **kwargs):
        da = kwargs['da'] if 'da' in kwargs else None
        pc = kwargs['pc'] if 'pc' in kwargs else None
        bn = kwargs['bn'] if 'bn' in kwargs else None
        mcs = kwargs['mcs'] if 'mcs' in kwargs else None

        if not pc and not bn:
            bn = self.target_bn
            if not bn:
                # todo empty parameter model
                raise KeyError('Undefined parameter model')

        if da:
            pass
        elif 'mcs' in kwargs:
            pass
        else:
            raise KeyError('da(Director) or a dict of model blueprint needed')

        if pc is None:
            hie = self.get_parameter_hierarchy(da=da)
            sm = dag.as_simulation_core(bn, hie=hie)
            pc = sm.generate(name, exo=kwargs['exo'] if 'exo' in kwargs else None)

        models = MultiModel(name, pars=pc)
        models.Class = self.Class

        for mod in self.models():
            name, proto, _ = mod
            sub_pc = pc.breed(name, proto)
            if mcs:
                m = mcs[proto].generate(name, pc=sub_pc)
            elif da.has_sim_model(proto):
                m = da.generate_model(name, proto, pc=sub_pc, da=da)
            else:
                raise KeyError("Unknown simulation model")

            models.append_child(m, self.ObsAllModels)
            if name in self.ObsModels or proto in self.ObsModels:
                models.add_observing_model(m)

        for interaction in self.Interactions:
            for m in models.select_all(interaction.Selector).values():
                m.add_listener(interaction.pass_checker(), interaction.pass_response())

        for act in self.ObsActors:
            models.add_observing_actor(act)

        for _, sel in self.Summaries.items():
            models.add_observing_selector(sel.clone())

        return models

    def get_y0_proto(self):
        return BranchY0()

    def get_y0s(self):
        y0s = BranchY0()
        for mod in self.models():
            name, _, y0 = mod
            y0s.append_child(name, y0)
        return y0s

    def to_json(self):
        js = dict()
        js['Class'] = self.Class
        js['Entries'] = [ent.to_json() for ent in self.Entries]
        js['Interactions'] = [inter.to_json() for inter in self.Interactions]
        return js

    @staticmethod
    def from_json(js):
        lyo = ModelLayout(js['Class'])
        for ent in js['Entries']:
            if 'Index' in ent:
                lyo.add_entry(ent['Name'], ent['Prototype'], ent['Y0'], **ent['Index'])
            else:
                lyo.add_entry(ent['Name'], ent['Prototype'], ent['Y0'])

        for inter in js['Interactions']:
            lyo.add_interaction_js(inter)
        return lyo

    def clone_model(self, mod_src, **kwargs):
        pass


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
