from complexism.misc.counter import count
from complexism.mcore import *
from .entries import RelationEntry
from .summariser import Summariser

__author__ = 'TimeWz667'
__all__ = ['ObsMultiModelStep', 'MultiModelStep']


class ObsMultiModelStep(Observer):
    def __init__(self):
        Observer.__init__(self)
        self.ObservingModels = list()
        self.ObservingSelectors = list()

    def add_observing_model(self, model):
        if model not in self.ObservingModels:
            self.ObservingModels.append(model)

    def add_observing_selector(self, sel):
        self.ObservingSelectors.append(sel)

    def update_dynamic_observations(self, model, flow, ti):
        pass

    def read_statics(self, model, tab, ti):
        s = model.Summariser

        tab.update(s.Impulses)
        if tab is self.Last:
            for sel in self.ObservingSelectors:
                sub = [m.Obs.Last for m in model.select_all(sel).values()]
                self.fill_table(sel, tab, sub)
        elif self.ExtMid:
            for sel in self.ObservingSelectors:
                sub = [m.Obs.Mid for m in model.select_all(sel).values()]
                self.fill_table(sel, tab, sub)

        for m in self.ObservingModels:
            mod = model.get_model(m)
            if tab is self.Last:
                tab.update({'{}@{}'.format(m, k): v for k, v in mod.Obs.Last.items() if k != 'Time'})
            elif self.ExtMid:
                tab.update({'{}@{}'.format(m, k): v for k, v in mod.Obs.Mid.items() if k != 'Time'})

    @staticmethod
    def fill_table(sel, tab, sub):
        dat = pd.DataFrame(sub)
        tab.update({"{}@{}".format(sel, k): v for k, v in dat.sum().items() if k != 'Time'})


class MultiModelStep(BranchModel):
    def __init__(self, name, pc=None, dt=0.5):
        BranchModel.__init__(self, name, pc, ObsMultiModelStep())
        self.Models = dict()
        self.Acceptors = set()
        self.Summariser = Summariser(name, dt=dt)

    def add_observing_selector(self, mod):
        self.Obs.add_observing_selector(mod)

    def add_observing_model(self, m):
        if m in self.Models:
            self.Obs.add_observing_model(m)

    def append(self, m):
        if m.Name not in self.Models:
            self.Models[m.Name] = m

    def link(self, src, tar):
        src = src if isinstance(src, RelationEntry) else RelationEntry(src)
        tar = tar if isinstance(tar, RelationEntry) else RelationEntry(tar)

        if src.Selector == self.Name:
            m_tar = self.select_all(tar.Selector)
            for kt, mt in m_tar.items():
                self.Acceptors.add(kt)
                mt.listen(src.Selector, src.Parameter, tar.Parameter)

        elif tar.Selector == self.Name:
            self.Summariser.add_task(src.Selector, src.Parameter)
        else:
            ent = RelationEntry((self.Name, True, src.indicator()), parse=False)
            self.link(src, ent)
            self.link(ent, tar)

    def read_y0(self, y0, ti):
        if not y0:
            return
        for k, m in self.Models.items():
            m.read_y0(y0=y0[k], ti=ti)

    def reset_impulse(self, ti):
        self.cross_impulse(ti)

    @count()
    def do_request(self, req):
        if req.What == 'Summarise':
            self.cross_impulse(req.When)
            self.Summariser.execute_event()
            self.Summariser.drop_next()

    def find_next(self):
        for k, model in self.all_models().items():
            for req in model.Next:
                self.Requests.append_event(req.Event, k, self.Name)
        self.Requests.append_event(self.Summariser.Next,'Summariser', self.Name)

    def cross_impulse(self, ti):
        self.Summariser.read_tasks(self, ti)
        for k in self.Acceptors:
            m = self.Models[k]
            m.impulse_foreign(self.Summariser, ti)

    def all_models(self):
        return self.Models

    def get_model(self, k):
        return self.Models[k]

    def clone(self, **kwargs):
        pass
