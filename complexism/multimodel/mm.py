from collections import OrderedDict
from complexism.misc.counter import count
from complexism.mcore import BranchModel, Observer, BranchY0


__author__ = 'TimeWz667'
__all__ = ['ObsMultiModel', 'MultiModel']


class ObsMultiModel(Observer):
    def __init__(self):
        Observer.__init__(self)
        self.ObservingModels = list()
        self.ObservingActors = list()

    def add_observing_model(self, model):
        if model not in self.ObservingModels:
            self.ObservingModels.append(model)

    def add_observing_actor(self, actor):
        if actor not in self.ObservingActors:
            self.ObservingActors.append(actor)

    def update_dynamic_observations(self, model, flow, ti):
        for m in self.ObservingModels:
            mod = model.get_model(m)
            flow.update({'{}:{}'.format(m, k): v for k, v in mod.Observer.Flow.items() if k != 'Time'})

    def read_statics(self, model, tab, ti):
        for m in self.ObservingModels:
            mod = model.get_model(m)
            if tab is self.Last:
                tab.update({'{}:{}'.format(m, k): v for k, v in mod.Observer.Last.items() if k != 'Time'})
            elif self.ExtMid:
                tab.update({'{}:{}'.format(m, k): v for k, v in mod.Observer.Mid.items() if k != 'Time'})

        for be in self.ObservingActors:
            model.Actors[be].fill(tab, model, ti)


class MultiModel(BranchModel):
    def __init__(self, name, pars=None):
        BranchModel.__init__(self, name, pars=pars, obs=ObsMultiModel(), y0_class=BranchY0)
        self.Children = dict()
        self.Actors = OrderedDict()

    def append_child(self, model, obs=True):
        m = model.Name
        if m not in self.Children:
            self.Children[m] = model
            if obs:
                self.Observer.add_observing_model(m)
        else:
            raise AttributeError('Duplicated model name')

    def append_actor(self, act):
        if act.Name not in self.Actors:
            self.Actors[act.Name] = act
            self.Scheduler.add_atom(act)
        else:
            raise AttributeError('Duplicated atom name')

    def add_observing_model(self, m):
        if m in self.Children:
            self.Observer.add_observing_model(m)
        else:
            raise KeyError('Model {} does not exist'.format(m))

    def add_observing_actor(self, act):
        if act in self.Actors:
            self.Observer.add_observing_actor(act)
        else:
            raise KeyError('Actor {} does not exist'.format(act))

    @count()
    def do_request(self, req):
        nod, evt, time = req.Who, req.Event, req.When
        try:
            act = self.Actors[nod]
            act.approve_event(evt)
            act.operate(self)
        except KeyError as e:
            raise e

    def all_models(self):
        return self.Children

    def get_model(self, k):
        return self.Children[k]

    def clone(self, **kwargs):
        pass

    def to_json(self):
        pass
