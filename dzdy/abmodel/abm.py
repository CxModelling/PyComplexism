from dzdy.mcore import Observer, LeafModel, Request
from dzdy.abmodel import Population, ForeignShock, ForeignAddShock
from collections import namedtuple, OrderedDict

__author__ = 'TimeWz667'
__all__ = ['MetaABM', 'ObsABM', 'AgentBasedModel']


RecordABM = namedtuple('RecordABM', ('Ag', 'Tr', 'Time'))
MetaABM = namedtuple('MetaABM', ('PC', 'DC', 'Prototype'))


class ObsABM(Observer):
    def __init__(self):
        Observer.__init__(self)
        self.ObsSt = list()
        self.ObsTr = list()
        self.Bes = list()
        self.Recs = list()
        self.Sums = list()

    def add_obs_state(self, st):
        self.ObsSt.append(st)

    def add_obs_transition(self, tr):
        self.ObsTr.append(tr)

    def add_obs_function(self, func):
        self.Sums.append(func)

    def add_obs_behaviour(self, beh):
        self.Bes.append(beh)

    def single_observe(self, model, ti):
        self.Last = OrderedDict()
        self.Last['Time'] = ti

        for st in self.ObsSt:
            self.Last['P_{}'.format(st.Name)] = model.Pop.count(st)

        for tr in self.ObsTr:
            self.Last['I_{}'.format(tr.Name)] = sum(rec.Tr == tr for rec in self.Recs)

        for be in self.Bes:
            model.Behaviours[be].fill(self.Last, model, ti)

        for fun in self.Sums:
            fun(self.Last, model, ti)
        self.Recs = list()

    def record(self, ag, tr, ti):
        self.Recs.append(RecordABM(ag.Name, tr, ti))


class AgentBasedModel(LeafModel):
    def __init__(self, name, dc, pc, meta=None, ag_prefix='Ag'):
        LeafModel.__init__(self, name, meta)
        self.DCore = dc
        self.PCore = pc
        self.Obs = ObsABM()
        self.Pop = Population(dc, ag_prefix)
        self.Behaviours = OrderedDict()

    def __getitem__(self, item):
        return self.Obs.Last[item]

    def add_obs_state(self, st):
        if st in self.DCore.States:
            self.Obs.add_obs_state(self.DCore.States[st])

    def add_obs_transition(self, tr):
        if tr in self.DCore.Transitions:
            self.Obs.add_obs_transition(self.DCore.Transitions[tr])

    def add_obs_function(self, fun):
        self.Obs.add_obs_function(fun)

    def add_obs_behaviour(self, be):
        if be in self.Behaviours:
            self.Obs.add_obs_behaviour(be)

    def listen(self, mod_src, par_src, tar, par_tar=None):
        try:
            be = self.Behaviours[tar]
            be.set_source(mod_src, par_src, par_tar)
        except KeyError:
            ForeignShock.decorate('{}->{}'.format(par_src, tar), self,
                                  par_src=par_src, mod_src=mod_src, t_tar=tar)

    def listen_multi(self, mod_src_all, par_src, tar, par_tar=None):
        try:
            be = self.Behaviours[tar]
            for mod in mod_src_all:
                be.set_source(mod, par_src, par_tar)
        except KeyError:

            name = '{}->{}'.format(par_src, tar)
            m = ForeignAddShock.decorate(name, self, t_tar=tar)
            for mod in mod_src_all:
                m.set_source(mod, par_src, par_tar)

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
        return self.Pop.Agents.values()

    def output(self):
        return self.Obs.observation

    def clone(self, **kwargs):
        # todo
        return
