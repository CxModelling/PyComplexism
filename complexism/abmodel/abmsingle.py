from complexism.mcore import Observer, LeafModel
from complexism.element import Request
from complexism.abmodel import GenericAgent
from collections import namedtuple, OrderedDict, Counter


__author__ = 'TimeWz667'
__all__ = ['SingleIndividualABM']


RecordABM = namedtuple('RecordABM', ('Tr', 'Time'))


class ObsSingleAgent(Observer):
    def __init__(self):
        Observer.__init__(self)
        self.Bes = list()
        self.Recs = list()

    def add_obs_behaviour(self, beh):
        self.Bes.append(beh)

    def update_dynamic_Observations(self, model, flow, ti):
        trs = Counter([rec.Tr for rec in self.Recs])
        flow.update(trs)
        self.Recs.clear()

    def read_statics(self, model, tab, ti):
        tab.update(model.Agent.to_data())

        for be in self.Bes:
            model.Behaviours[be].fill(tab, model, ti)

    def record(self, tr, ti):
        self.Recs.append(RecordABM(tr.Name, ti))


class SingleIndividualABM(LeafModel):
    def __init__(self, name, agent: GenericAgent):
        LeafModel.__init__(self, name, ObsSingleAgent())
        self.Agent = agent
        self.Behaviours = OrderedDict()

    def add_obs_behaviour(self, be):
        if be in self.Behaviours:
            self.Obs.add_obs_behaviour(be)

    def add_behaviour(self, be):
        if be.Name not in self.Behaviours:
            self.Behaviours[be.Name] = be

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
        self.Agent.initialise(ti)
        for be in self.Behaviours.values():
            be.register(self.Agent, ti)

    def reset(self, ti):
        self.Agent.reset(ti)
        for be in self.Behaviours.values():
            be.initialise(self, ti)

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

    def find_next(self):
        # to be parallel
        for k, be in self.Behaviours.items():
            nxt = be.next
            self.Requests.append_event(nxt, who=k, where=self.Name)

        nxt = self.Agent.Next
        self.Requests.append_event(nxt, who=self.Agent.Name, where=self.Name)

    def do_request(self, req: Request):
        nod, evt, time = req.Who, req.Event, req.When
        if nod in self.Behaviours:
            be = self.Behaviours[nod]
            be.exec(self, evt)
        else:
            tr = evt.Todo
            self.Agent.fetch_event(evt)
            self.Obs.record(tr, time)
            bes = self.check_tr(self.Agent, tr)
            self.Agent.execute_event()
            self.Agent.drop_next()
            self.impulse_tr(bes, self.Agent, time)
            self.Agent.update_time(time)

    def __len__(self):
        return 1

    def clone(self, **kwargs):
        # todo
        return
