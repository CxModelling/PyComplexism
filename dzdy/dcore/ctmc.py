import json
from dzdy.dcore.dynamics import *


class ModelCTMC(AbsDynamicModel):
    def __init__(self, name, sts, trs, tars, js):
        AbsDynamicModel.__init__(self, name, js)
        self.States = sts
        self.Transitions = trs
        self.Targets = tars

    @property
    def WellDefinedStates(self):
        return self.States

    def get_reachable(self, sts):
        return self.States

    def get_transitions(self, fr):
        return self.Targets[fr]

    def get_transition(self, fr, to):
        return [tr for tr in self.Targets[fr] if tr.State == to]

    def isa(self, s0, s1):
        return s0 is s1

    def get_state_space(self):
        return self.States

    def get_transition_space(self):
        return self.Transitions

    def __getitem__(self, item):
        return self.States[item]

    def exec(self, st, evt):
        return evt.State

    def __deepcopy__(self):
        return BlueprintCTMC.from_json(self.to_json())


class BlueprintCTMC(AbsBlueprint):
    @staticmethod
    def from_json(js):
        if isinstance(js, str):
            js = json.loads(js)

        bp = BlueprintCTMC(js['ModelName'])
        for st in js['States']:
            bp.add_state(st)
        for tr, trd in js['Transitions'].items():
            bp.add_transition(tr, trd['To'], trd['Dist'])
        for fr, trs in js['Targets'].items():
            for tr in trs:
                bp.link_state_transition(fr, tr)
        return bp

    def __init__(self, name):
        AbsBlueprint.__init__(self, name)
        self.States = list()
        self.Transitions = dict()  # Name -> (event, distribution)
        self.Targets = dict()  # StateName -> TransitionNames

    def add_state(self, state):
        if state in self.States:
            return False

        self.States.append(state)
        self.Targets[state] = list()
        return True

    def add_transition(self, tr, to, dist=None):
        """
        Define a new transition
        :param tr: name of transition
        :param to: name of targeted state
        :param dist: name of distribution, need to be in the parameter core
        :return: true if succeed
        """
        self.add_state(to)
        if not dist:
            dist = tr

        self.Transitions[tr] = {'To': to, 'Dist': dist}
        return True

    def link_state_transition(self, state, tr):
        self.add_state(state)

        if tr not in self.Transitions:
            raise KeyError('Transition {} does not exist'.format(tr))
        self.Targets[state].append(tr)
        return True

    def to_json(self):
        js = dict()
        js['ModelType'] = 'CTMC'
        js['ModelName'] = self.Name
        js['States'] = self.States
        js['Transitions'] = self.Transitions
        js['Targets'] = self.Targets
        return js

    def __repr__(self):
        return str(self.to_json())

    def __str__(self):
        return str(self.to_json())

    def generate_model(self, pc, mn=None):
        sts = {k: State(k) for k in self.States}
        trs = dict()
        for name, tr in self.Transitions.items():
            trs[name] = Transition(name, sts[tr['To']], pc.get_distribution(tr['Dist']))

        tars = {stv: [trs[tar] for tar in self.Targets[stk]] for stk, stv in sts.items()}

        mn = mn if mn else self.Name

        js = self.to_json()

        mod = ModelCTMC(mn, sts, trs, tars, js)
        for val in sts.values():
            val.Model = mod
        return mod

    def is_compatible(self, pc):
        return all([tr['Dist'] in pc.Distributions for tr in self.Transitions.values()])
