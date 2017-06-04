from dzdy.mcore import Observer, LeafModel, Request
from dzdy.abmodel import Population, ForeignShock
from collections import namedtuple, OrderedDict

__author__ = 'TimeWz667'


RecordABM = namedtuple("RecordABM", ("Ag", "Tr", "Time"))


class ObsABM(Observer):
    def __init__(self):
        Observer.__init__(self)
        self.ObsSt = list()
        self.ObsTr = list()
        self.Bes = list()
        self.Recs = list()
        self.Sums = list()

    def add_obs_atr(self, st):
        self.ObsSt.append(st)

    def add_obs_tr(self, tr):
        self.ObsTr.append(tr)

    def add_obs_func(self, func):
        self.Sums.append(func)

    def add_obs_behaviour(self, beh):
        self.Bes.append(beh)

    def single_observe(self, model, ti):
        self.Last = OrderedDict()
        self.Last["Time"] = ti

        for st in self.ObsSt:
            self.Last['P.{}'.format(st.Value)] = model.Pop.count(st)

        for tr in self.ObsTr:
            self.Last['I.{}'.format(tr.Name)] = sum(rec.Tr == tr for rec in self.Recs)

        for be in self.Bes:
            model.Behaviours[be].fill(self.Last, model, ti)

        for fun in self.Sums:
            fun(self.Last, model, ti)
        self.Recs = list()

    def record(self, ag, tr, ti):
        self.Recs.append(RecordABM(ag.Name, tr, ti))


class AgentBasedModel(LeafModel):
    def __init__(self, name, dcore, **kwargs):
        LeafModel.__init__(self, name)
        self.Obs = ObsABM()
        self.Pop = Population(dcore, **kwargs)
        self.DCore = dcore
        self.Behaviours = OrderedDict()

    def __getitem__(self, item):
        return self.Obs.Last[item]

    def set_seed(self, seed=1167):
        self.DCore.seed = 1167

    def add_obs_state(self, st):
        if st in self.DCore.States:
            self.Obs.add_obs_atr(self.DCore.States[st])

    def add_obs_tr(self, tr):
        if tr in self.DCore.Transitions:
            self.Obs.add_obs_tr(self.DCore.Transitions[tr])

    def add_obs_fun(self, fun):
        self.Obs.add_obs_func(fun)

    def add_obs_be(self, be):
        if be in self.Behaviours:
            self.Obs.add_obs_behaviour(be)

    def listen(self, src_model, src_value, src_target):
        ForeignShock.decorate(src_value, self, src_value=src_value, src_model=src_model, src_target=src_target)

    def read_y0(self, y0, ti):
        if y0:
            for atr, num in y0.items():
                self.make_agent(atr, num, ti)

    def reset(self, ti):
        for be in self.Behaviours.values():
            be.initialise(self, ti)
        for ag in self.Pop.Agents.values():
            ag.initialise(ti)
        self.Obs.single_observe(self, ti)

    def make_agent(self, atr, n, ti):
        ags = self.Pop.add_agent(atr, n)
        for ag in ags:
            for be in self.Behaviours.values():
                be.register(ag, ti)

    def check_in(self, ag):
        return (be for be in self.Behaviours.values() if be.check_in(ag))

    def impulse_in(self, bes, ag, ti):
        for be in bes:
            be.impulse_in(self, ag, ti)

    def check_out(self, ag):
        return (be for be in self.Behaviours.values() if be.check_out(ag))

    def impulse_out(self, bes, ag, ti):
        for be in bes:
            be.impulse_out(self, ag, ti)

    def impulse_foreign(self, fore, ti):
        res = False
        for be in self.Behaviours.values():
            if be.check_foreign(fore):
                res = True
                be.impulse_foreign(self, fore, ti)

        if res:
            self.drop_next()
        return res

    def check_tr(self, ag, tr):
        return [be for be in self.Behaviours.values() if be.check_tr(ag, tr)]

    def impulse_tr(self, bes, ag, ti):
        for be in bes:
            be.impulse_tr(self, ag, ti)

    def birth(self, atr, ti, n=1, info=None):
        if info:
            ags = self.Pop.add_agent(atr, n, info=info)
        else:
            ags = self.Pop.add_agent(atr, n)
        for ag in ags:
            for be in self.Behaviours.values():
                be.register(ag, ti)
            bes = self.check_in(ag)
            ag.initialise(ti)
            self.impulse_in(bes, ag, ti)
        return ags

    def kill(self, i, ti):
        ag = self.Pop[i]
        bes = self.check_out(ag)
        self.Pop.remove_agent(i)
        self.impulse_out(bes, ag, ti)

    def observe(self, ti):
        self.Obs.observe(self, ti)

    def find_next(self):
        # to be parallel
        for k, be in self.Behaviours.items():
            nxt = be.next
            self.Requests.append_src(k, nxt, nxt.Time)

        for k, ag in self.Pop.Agents.items():
            nxt = ag.next
            self.Requests.append_src(k, nxt, nxt.Time)

    def do_request(self, req: Request):
        nod, evt, time = req.Node, req.Event, req.Time
        if nod in self.Behaviours:
            be = self.Behaviours[nod]
            be.exec(self, evt)
        else:
            ag = self.Pop[nod]
            tr = evt.Transition
            self.Obs.record(ag, tr, time)
            bes = self.check_tr(ag, tr)
            ag.exec(evt)
            self.impulse_tr(bes, ag, time)
            ag.update(time)

    def __len__(self):
        return len(self.Pop.Agents)

    @property
    def agents(self):
        for ag in self.Pop.Agents.values():
            yield ag

    def to_json(self):
        # todo
        pass

    def output(self):
        return self.Obs.observation