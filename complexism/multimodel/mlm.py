from complexism.mcore import BranchModel, BranchY0, Observer


class ObsMLModel(Observer):
    def __init__(self):
        Observer.__init__(self)
        self.ObservingModels = list()
        self.Actor = list()

    def add_observing_actor(self, actor):
        self.Actor.append(actor)

    def add_observing_model(self, model):
        if model not in self.ObservingModels:
            self.ObservingModels.append(model)

    def update_dynamic_observations(self, model, flow, ti):
        for m in self.ObservingModels:
            mod = model.get_model(m)
            flow.update({'{}.{}'.format(m, k): v for k, v in mod.Observer.Flow.items() if k != 'Time'})

    def read_statics(self, model, tab, ti):
        for m in self.ObservingModels:
            mod = model.get_model(m)
            if tab is self.Last:
                tab.update({'{}.{}'.format(m, k): v for k, v in mod.Observer.Last.items() if k != 'Time'})
            elif self.ExtMid:
                tab.update({'{}.{}'.format(m, k): v for k, v in mod.Observer.Mid.items() if k != 'Time'})


class MLModelY0(BranchY0):
    def __init__(self):
        BranchY0.__init__(self)

    def append_child(self, key, chd):
        self.ChildrenY0[key] = chd

    def match_model(self, model):
        pass

    def define(self, *args, **kwargs):
        pass

    @staticmethod
    def from_source(src):
        y0 = MLModelY0()
        for k, v in src.items():
            y0.append_child(k, v)
        return y0


class MultiLevelModel(BranchModel):
    def __init__(self, name, env=None):
        BranchModel.__init__(self, name, env=env, obs=ObsMLModel(), y0_class=MLModelY0)
        self.SubModels = dict()
        self.Actors = dict()

    def all_models(self) -> dict:
        return self.SubModels

    def get_model(self, k):
        return self.SubModels[k]

    def append(self, model, obs=True):
        m = model.Name
        if m not in self.SubModels:
            self.SubModels[m] = model
        else:
            raise AttributeError('Duplicated model name')

        if obs:
            self.add_observing_model(m)

    def add_observing_model(self, m):
        if m in self.SubModels:
            self.Observer.add_observing_model(m)

    def append_actor(self, act):
        if act.Name not in self.Actors:
            self.Actors[act.Name] = act
        else:
            raise AttributeError('Duplicated actor name')

    def do_request(self, req):
        nod, evt, time = req.Who, req.Event, req.When
        try:
            act = self.Actors[nod]
            act.approve_event(evt)
            act.operate(self)
            # act.append(self)
        except KeyError as e:
            raise e

    def read_y0(self, y0, ti):
        if not y0:
            return
        for k, m in self.SubModels.items():
            m.read_y0(y0[k], ti=ti)

    def find_next(self):
        for k, be in self.Actors.items():
            self.request(be.Next, k)
