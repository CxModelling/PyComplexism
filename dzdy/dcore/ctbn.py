import json
from itertools import product
from collections import OrderedDict
from dzdy.dcore.dynamics import *

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

    __str__ = __repr__

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

    def get_reachable(self, sts):
        sts = [self[st] for st in sts]
        to_check = list(sts)
        checked = set()
        reachable = {st.Name: st for st in sts}

        while to_check:
            st = to_check.pop()
            for tr in st.next_transitions():
                st_new = st.exec(tr)
                reachable[st_new.Name] = st_new
                if st_new not in checked:
                    to_check.append(st_new)

            checked.add(st)
        return reachable

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


class BlueprintCTBN(AbsBlueprint):
    @staticmethod
    def from_json(js):
        if isinstance(js, str):
            js = json.loads(js)
        bp = BlueprintCTBN(js['ModelName'])
        if 'Order' in js:
            for ms in js['Order']:
                bp.add_microstate(ms, js['Microstates'][ms])
        for ms, vs in js['Microstates'].items():
            bp.add_microstate(ms, vs)
        for st, std in js['States'].items():
            bp.add_state(st, **std)
        for tr, trd in js['Transitions'].items():
            bp.add_transition(tr, trd['To'], trd['Dist'])
        for fr, trs in js['Targets'].items():
            for tr in trs:
                bp.link_state_transition(fr, tr)
        return bp

    def __init__(self, name):
        AbsBlueprint.__init__(self, name)
        self.Microstates = OrderedDict()  # Name -> array of states
        self.States = dict()  # Nick name -> combination of microstates
        self.Transitions = dict()  # Name -> (event, distribution)
        self.Targets = dict()  # StateName -> TransitionNames

    def add_microstate(self, mst, arr):
        if mst in self.Microstates:
            return False
        self.Microstates[mst] = arr

    def add_state(self, state, **kwargs):
        if state in self.States:
            return False

        if not kwargs:
            return False
        mss = dict()
        for k in self.Microstates.keys():
            if k not in kwargs:
                continue
            v = kwargs[k]
            if isinstance(v, str):
                if v in self.Microstates[k]:
                    mss[k] = v
                else:
                    raise KeyError('Microstate does not exist')

            else:
                try:
                    mss[k] = self.Microstates[k][v]
                except KeyError:
                    raise IndexError('Wrong Index')
        self.States[state] = mss
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

    def link_state_transition(self, st, tr):
        self.add_state(st)
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
        js['Microstates'] = dict(self.Microstates)
        js['States'] = dict(self.States)
        js['Transitions'] = dict(self.Transitions)
        js['Targets'] = dict(self.Targets)
        js['Order'] = list(self.Microstates.keys())
        return js

    def __repr__(self):
        return str(self.to_json())

    def generate_model(self, pc, mn=None):
        mss = {k: MicroNode(k, v) for k, v in self.Microstates.items()}

        def align_sts(det):
            ods = OrderedDict([(ms, det[ms]) for ms in self.Microstates.keys() if ms in det])
            return str(ods)

        nat = {align_sts(nodes): st for st, nodes in self.States.items()}
        iat = dict()
        for st in product(*[val + [None] for val in self.Microstates.values()]):
            arr = [(k, v) for k, v in zip(self.Microstates.keys(), st) if v]
            od = OrderedDict(arr)
            try:
                name = nat[str(od)]
            except KeyError:
                name = '[{}]'.format(', '.join('{}={}'.format(*v) for v in arr))
                nat[str(od)] = name
            ad = [mss[k][v] for k, v in od.items()]
            iat[name] = ad, od

        sts = {k: State(k) for k in iat.keys()}
        wds = [k for k, v in iat.items() if len(v[1]) == len(mss)]
        subs = {sts[k]: [sts[s] for s, sv in iat.items() if set(sv[0]) <= set(iat[k][0])] for k in wds}

        ls = dict()
        for fr in wds:
            fr_st = iat[fr][1]
            lif = dict()
            for tr, tr_st in iat.items():
                to_st = fr_st.copy()
                to_st.update(tr_st[1])
                to = nat[str(to_st)]
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

        mn = mn if mn else self.Name

        js = self.to_json()

        mod = ModelCTBN(mn, mss, sts, wds, subs, ls, trs, tars, js)
        for val in sts.values():
            val.Model = mod
        return mod

    def is_compatible(self, pc):
        return all([tr['Dist'] in pc.Distributions for tr in self.Transitions.values()])
