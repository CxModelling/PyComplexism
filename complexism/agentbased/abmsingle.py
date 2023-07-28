from collections import namedtuple, OrderedDict
from misc.counter import count
from mcore import Observer, LeafModel
from element import Request
from complexism.agentbased import GenericAgent


__author__ = 'TimeWz667'
__all__ = ['SingleIndividualABM']


Record = namedtuple('Record', ('Tr', 'Time'))


class ObsSingleAgent(Observer):
    def __init__(self):
        Observer.__init__(self)
        self.Bes = list()
        self.Ats = list()
        self.Recs = list()

    def add_observing_attribute(self, atr):
        self.Ats.append(atr)

    def add_observing_behaviour(self, beh):
        self.Bes.append(beh)

    def update_dynamic_observations(self, model, flow, ti):
        # trs = Counter([rec.Tr for rec in self.Recs])
        # flow.update(trs)
        self.Recs.clear()

    def read_statics(self, model, tab, ti):
        ats = model.Agent.to_data()
        ats = {k: ats[k] for k in self.Ats}
        tab.update(ats)

        for be in self.Bes:
            model.Behaviours[be].fill(tab, model, ti)

    def record(self, tr, ti):
        self.Recs.append(Record(tr, ti))


class SingleIndividualABM(LeafModel):
    def __init__(self, name, agent: GenericAgent, pars=None):
        LeafModel.__init__(self, name, pars=pars, obs=ObsSingleAgent())
        self.Agent = agent
        self.Scheduler.add_atom(agent)
        self.Behaviours = OrderedDict()

    def add_observing_attribute(self, atr):
        self.Observer.add_observing_attribute(atr)

    def add_observing_behaviour(self, be):
        if be in self.Behaviours:
            self.Observer.add_observing_behaviour(be)

    def add_behaviour(self, be):
        if be.Name not in self.Behaviours:
            self.Behaviours[be.Name] = be
            self.Scheduler.add_atom(be)

    def read_y0(self, y0, ti):
        for be in self.Behaviours.values():
            be.register(self.Agent, ti)

    def preset(self, ti):
        self.Agent.initialise(model=self, ti=ti)
        for be in self.Behaviours.values():
            be.preset(self, ti, model=self)
        self.Scheduler.reschedule_all()

    def reset(self, ti):
        self.Agent.reset(model=self, ti=ti)
        for be in self.Behaviours.values():
            be.reset(self, ti, model=self)
        self.Scheduler.reschedule_all_actors()

    def trigger_external_impulses(self, disclosure, model, time):
        res = False
        for be in self.Behaviours.values():
            if be.check_foreign(model):
                res = True
                be.impulse_foreign(self, model, time)

        if res:
            self.exit_cycle()
        return res

    def shock(self, time, action, **values):
        if action == 'impulse':
            try:
                be = self.Behaviours[action]
                be.shock(time, self, action, values)
            except KeyError:
                raise KeyError('Unknown target')
            except AttributeError as e:
                raise e

    def check_tr(self, ag, tr):
        return [be for be in self.Behaviours.values() if be.check_tr(ag, tr)]

    def impulse_tr(self, bes, ag, ti):
        for be in bes:
            be.impulse_tr(self, ag, ti)

    @count()
    def do_request(self, req: Request):
        nod, evt, time = req.Who, req.Event, req.When
        if nod in self.Behaviours:
            be = self.Behaviours[nod]
            be.exec(self, evt)
        else:
            tr = evt.Todo
            self.Agent.approve_event(evt)
            self.Observer.record(tr, time)
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
