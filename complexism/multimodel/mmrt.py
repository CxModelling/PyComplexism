import networkx as nx
from complexism.misc.counter import count
from complexism.mcore import *
from .entries import RelationEntry


__author__ = 'TimeWz667'
__all__ = ['ObsMultiModel', 'MultiModel']


class ObsMultiModel(Observer):
    def __init__(self):
        Observer.__init__(self)
        self.ObservingModels = list()

    def add_observing_model(self, model):
        if model not in self.ObservingModels:
            self.ObservingModels.append(model)

    def update_dynamic_observations(self, model, flow, ti):
        for m in self.ObservingModels:
            mod = model.get_model(m)
            flow.update({'{}@{}'.format(m, k): v for k, v in mod.Observer.Flow.items() if k != 'Time'})

    def read_statics(self, model, tab, ti):
        for m in self.ObservingModels:
            mod = model.get_model(m)
            if tab is self.Last:
                tab.update({'{}@{}'.format(m, k): v for k, v in mod.Observer.Last.items() if k != 'Time'})
            elif self.ExtMid:
                tab.update({'{}@{}'.format(m, k): v for k, v in mod.Observer.Mid.items() if k != 'Time'})


class MultiModel(BranchModel):
    def __init__(self, name, env=None):
        BranchModel.__init__(self, name, env=env, obs=ObsMultiModel())
        self.Models = nx.MultiDiGraph()

    def add_observing_model(self, m):
        if m in self.Models:
            self.Observer.add_observing_model(m)

    def append(self, m):
        if m.Name not in self.Models:
            self.Models.add_node(m.Name, model=m)

    def link(self, src, tar, message=None, **kwargs):
        src = src if isinstance(src, RelationEntry) else RelationEntry(src)
        tar = tar if isinstance(tar, RelationEntry) else RelationEntry(tar)

        m_src = self.select_all(src.Selector)
        m_tar = self.select_all(tar.Selector)

        if src.is_single():
            ms = m_src.first()
            for kt, mt in m_tar.items():
                if ms is not mt:
                    mt.listen(ms.Name, message, src.Parameter, tar.Parameter, **kwargs)
                    self.Models.add_edge(ms.Name, mt.Name, par_src=src.Parameter, par_tar=tar.Parameter)

    def read_y0(self, y0, ti):
        if not y0:
            return
        for k, m in self.Models.nodes().data('model'):
            m.read_y0(y0=y0[k], ti=ti)

    def reset_impulse(self, ti):
        for s, nbd in self.Models.adjacency():
            src = self.get_model(s)
            for t in nbd.keys():
                tar = self.get_model(t)
                tar.impulse_foreign(src, 'update', ti)

    @count()
    def do_request(self, req):
        src = self.get_model(req.Who)
        for t, kb in self.Models[req.Who].items():
            # for _, atr in kb.items():
            tar = self.get_model(t)
            tar.impulse_foreign(src, req.Message, req.When)

    def find_next(self):
        pass

    def all_models(self):
        return dict(self.Models.nodes().data('model'))

    def get_model(self, k):
        return self.Models.nodes[k]['model']

    def clone(self, **kwargs):
        pass
