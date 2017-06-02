import json
from itertools import product
from collections import OrderedDict
from dcore.dynamics import *

__author__ = 'TimeWz667'


class MicroState:
    NullState = None

    def __init__(self, des):
        """
        The state with a short description
        :param des: a string for describing the state
        """
        self.Des = str(des)

    def __repr__(self):
        return self.Des

MicroState.NullState = MicroState("_")


class MicroNode:
    def __init__(self, des, mss):
        self.Des = des
        self.MicroStates = [MicroState(ms) for ms in mss]

    def index(self, st):
        try:
            return self.MicroStates.index(st)
        except ValueError:
            return None

    def __getitem__(self, i):
        if isinstance(i, int):
            try:
                return self.MicroStates[i]
            except IndexError:
                return MicroState.NullState
        else:
            for ms in self.MicroStates:
                if ms.Des == i:
                    return ms
            return MicroState.NullState

    def __repr__(self):
        return self.Des + str(self.MicroStates)

    def __iter__(self):
        return iter(self.MicroStates)


class ModelCTBN(AbsDynamicModel):
    def __init__(self, name, mss, sts, wds, subs, ls, trs, tars, js):
        AbsDynamicModel.__init__(self, name, js)
        self.Microstates = mss
        self.States = sts
        self.WellDefinedStates = wds
        self.Subsets = subs
        self.Links = ls
        self.Transitions = trs
        self.Targets = tars

    def get_transitions(self, fr):
        return self.Targets[fr]

    def get_transition(self, fr, to):
        return [tr for tr in self.Targets[fr] if tr.State == to]

    def isa(self, s0, s1):
        return s1 in self.Subsets[s0]

    def get_state_space(self):
        return {k: v for k, v in self.States.items() if k in self.WellDefinedStates}

    def get_transition_space(self):
        return self.Transitions

    def __getitem__(self, item):
        return self.States[item]

    def exec(self, st, tr):
        return self.Links[st][tr.State]

    def __deepcopy__(self):
        return BluePrintCTBN.from_json(self.to_json())


class BluePrintCTBN(AbsBluePrint):
    @staticmethod
    def from_json(js):
        js = json.loads(js)
        bp = BluePrintCTBN(js['ModelName'])
        for ms in js['Order']:
            bp.add_microstate(ms, js['Microstates'][ms])
        for st, (ms, desc) in js['States'].items():
            bp.add_state(st, desc, **ms)
        for tr, trd in js['Transitions'].items():
            bp.add_transition(tr, trd['To'], trd['Dist'])
        for fr, trs in js['Targets'].items():
            for tr in trs:
                bp.link_state_transition(fr, tr)
        return bp

    def __init__(self, name, sm):
        AbsBluePrint.__init__(self, name, sm)
        self.Microstates = OrderedDict()  # Name -> array of states
        self.States = OrderedDict()  # Nick name -> (conbination of microstates, description)
        self.Transitions = OrderedDict()  # Name -> (event, distribution)
        self.Targets = OrderedDict()  # StateName -> TransitionNames

    def add_microstate(self, mst, arr):
        if mst in self.Microstates:
            return False
        self.Microstates[mst] = arr

    def add_state(self, state, desc=None, **kwargs):
        if state in self.States:
            return False
        desc = desc if desc else state
        if not kwargs:
            return False
        mss = OrderedDict()
        for k in self.Microstates.keys():
            if k not in kwargs:
                continue
            v = kwargs[k]
            if isinstance(v, str):
                if v in self.Microstates[k]:
                    mss[k] = v
                else:
                    print('Microstate does not exist')
                    return False
            else:
                try:
                    mss[k] = self.Microstates[k][v]
                except KeyError:
                    print('Wrong Index')
                    return False
        self.States[state] = mss, desc
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
        if dist not in self.ExCore.Distributions:
            raise KeyError('Distribution {} does not exist'.format(dist))
        self.Transitions[tr] = {'To': to, 'Dist': dist}
        return True

    def link_state_transition(self, st, tr):
        if tr not in self.Transitions:
            raise KeyError('Transition {} does not exist'.format(tr))

        self.Targets[st].append(tr)
        return True

    def link_state_transitions(self, st, trs):
        try:
            for tr in trs:
                self.link_state_transition(st, tr)
        except KeyError as e:
            raise e
        else:
            return True

    def link_states_transition(self, sts, tr):
        try:
            for st in sts:
                self.link_state_transition(st, tr)
        except KeyError as e:
            raise e
        else:
            return True

    def to_json(self):
        js = dict()
        js['ModelType'] = 'CTBN'
        js['ModelName'] = self.Name
        js['Microstates'] = self.Microstates
        js['States'] = self.States
        js['Transitions'] = self.Transitions
        js['Targets'] = self.Targets
        js['Order'] = list(self.Microstates.keys())
        js = {'dcore': js, 'pcore': self.SimulationCore.DAG.to_json()}
        return json.dumps(js)

    def __repr__(self):
        return str(self.to_json())

    def generate_model(self, suffix=''):
        pc = self.SimulationCore.sample_core()
        mss = {k: MicroNode(k, v) for k, v in self.Microstates.items()}
        nat = {str(od): (n, desc) for n, (od, desc) in self.States.items()}
        iat = dict()
        for st in product(*[val + [None] for val in self.Microstates.values()]):
            arr = [(k, v) for k, v in zip(self.Microstates.keys(), st) if v]
            od = OrderedDict(arr)
            try:
                name, desc = nat[str(od)]
            except KeyError:
                name = desc = '[{}]'.format(', '.join('{}={}'.format(*v) for v in arr))
                nat[str(od)] = name, desc
            ad = [mss[k][v] for k, v in od.items()]
            iat[name] = desc, ad, od

        sts = {k: State(k, v[0], None) for k, v in iat.items()}
        wds = [k for k, v in iat.items() if len(v[1]) == len(mss)]
        subs = {sts[k]: [sts[s] for s, sv in iat.items() if set(sv[1]) <= set(iat[k][1])] for k in wds}

        ls = dict()
        for fr in wds:
            fr_st = iat[fr][2]
            lif = dict()
            for tr, tr_st in iat.items():
                to_st = fr_st.copy()
                to_st.update(tr_st[2])
                to, _ = nat[str(to_st)]
                lif[sts[tr]] = sts[to]
            ls[sts[fr]] = lif

        trs = dict()
        for name, tr in self.Transitions.items():
            trs[name] = Transition(name, sts[tr['To']], pc.get_distribution(tr['Dist']))

        tars = {sts[wd]: list() for wd in wds}
        for fr, ts in self.Targets.items():
            fr = sts[fr]
            for k, v in tars.items():
                if fr in subs[k]:
                    v += [trs[tr] for tr in ts]

        mn = '{}_{}'.format(self.Name, suffix) if suffix else self.Name
        js = dict()
        js['ModelType'] = 'CTBN'
        js['ModelName'] = mn
        js['Microstates'] = self.Microstates
        js['States'] = self.States
        js['Transitions'] = {name: {'To': tr.State.Value, 'Dist': str(tr.Dist)} for name, tr in trs.items()}
        js['Targets'] = self.Targets
        js['Order'] = list(self.Microstates.keys())

        mod = ModelCTBN(mn, mss, sts, wds, subs, ls, trs, tars, js)
        for val in sts.values():
            val.Model = mod
        return mod
