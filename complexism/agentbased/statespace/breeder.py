from complexism.agentbased import GenericBreeder
import complexism.dcore as ss
from .agent import StSpAgent

__author__ = 'TimeWz667'


class StSpBreeder(GenericBreeder):
    def __init__(self, name, group, pc_parent, dc, **kwargs):
        GenericBreeder.__init__(self, name=name, group=group, pc_parent=pc_parent, **kwargs)
        if isinstance(dc, ss.AbsDynamicModel):
            self.DCore = dc
        else:
            self.DCore = dc.generate_model(name, **self.PCore.get_samplers())

        self.WStates = {wd: self.DCore[wd] for wd in self.DCore.WellDefinedStates}

    def _filter_attributes(self, kw):
        st = self.WStates[kw['st']]
        sts = {'st': st}
        del kw['st']
        return sts, kw

    def _new_agent(self, name, pars, **kwargs):
        return StSpAgent(name, kwargs['st'], pars=pars)

    def count(self, ags, **kwargs):
        try:
            st = kwargs['st']
        except KeyError:
            return len(ags)

        try:
            st = self.DCore[st] if isinstance(st, str) else st
            return sum(st in ag for ag in ags)
        except KeyError:
            return 0
