from .behaviour import TimeIndBehaviour
from .trigger import ForeignTrigger

__author__ = 'TimeWz667'
__all__ = ['ForeignListener', 'MultiForeignListener', 'Immigration']


class ForeignListener(TimeIndBehaviour):
    def __init__(self, name, mod_src, msg, par_src, par_tar, **kwargs):
        tri = ForeignTrigger(model=mod_src, msg=msg)
        TimeIndBehaviour.__init__(self, name, tri)
        self.Model = mod_src
        self.Source = par_src
        self.Target = par_tar
        self.Default = kwargs['default'] if 'default' in kwargs else 0
        self.Value = self.Default

    def set_source(self, mod_src, par_src, msg):
        self.Model = mod_src
        self.Source = par_src
        self.Trigger.add_source(mod_src, msg)

    def initialise(self, model, ti):
        self.Value = self.Default
        model[self.Target] = self.Value

    def register(self, ag, ti):
        pass

    def impulse_foreign(self, model, fore, message, ti, **kwargs):
        self.Value = fore.get_snapshot(self.Source, ti)
        model[self.Target] = self.Value

    @staticmethod
    def decorate(name, model, **kwargs):
        if 'mod_src' not in kwargs:
            kwargs['mod_src'] = None
        if 'par_src' not in kwargs:
            kwargs['par_src'] = None

        model.Behaviours[name] = ForeignListener(name, **kwargs)

    def match(self, be_src, ags_src, ags_new, ti):
        self.Value = be_src.Value

    def __repr__(self):
        opt = self.Name, '{}@{}'.format(self.Model, self.Source), self.Target, self.Value
        return 'Foreign({}, From ={}, To={}, Value={})'.format(*opt)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value
        return obs


class MultiForeignListener(TimeIndBehaviour):
    def __init__(self, name, mod_par_src, par_tar, **kwargs):
        tri = ForeignSetTrigger(mps=mod_par_src)
        TimeIndBehaviour.__init__(self, name, tri)
        self.Models = dict(mod_par_src)
        self.Target = par_tar
        self.Default = kwargs['default'] if 'default' in kwargs else 0
        self.Values = {k: self.Default for k in self.Models.keys()}

    def set_source(self, mod_src, par_src):
        self.Trigger.append(mod_src, par_src)
        self.Models[mod_src] = par_src
        self.Values[mod_src] = self.Default

    def initialise(self, model, ti):
        self.Values = {k: self.Default for k, v in self.Values.items()}
        model[self.Target] = self.Values

    def register(self, ag, ti):
        pass

    def impulse_foreign(self, model, fore, message, ti, **kwargs):
        key = fore.Name
        value = fore.get_snapshot(self.Models[key], ti)
        self.Values[key] = value
        model[self.Target] = self.Values

    @staticmethod
    def decorate(name, model, **kwargs):
        if 'mod_par_src' not in kwargs:
            kwargs['mod_par_src'] = None

        model.Behaviours[name] = MultiForeignListener(name, **kwargs)

    def match(self, be_src, ags_src, ags_new, ti):
        self.Models = dict(be_src.Models)
        self.Values = dict(be_src.Value)

    def __repr__(self):
        opt = self.Name, self.Target, sum(self.Values.values())
        return 'MultiForeign({}, To={}, Value={})'.format(*opt)

    def fill(self, obs, model, ti):
        obs[self.Name] = sum(self.Values.values())
        return obs


class Immigration(TimeIndBehaviour):
    def __init__(self, name, mod_src=None, par_src=None, im_info=None):
        trigger = ForeignTrigger(model=None, loc=None)
        TimeIndBehaviour.__init__(self, name, trigger)
        self.Model = mod_src
        self.Source = par_src
        self.ImInfo = dict(im_info) if im_info else dict()
        self.ImN = 0

    def set_source(self, mod_src, par_src):
        self.Trigger.append(mod_src, par_src)

    def initialise(self, model, ti):
        self.ImN = 0

    def register(self, ag, ti):
        pass

    def impulse_foreign(self, model, fore, message, ti, **kwargs):
        self.ImN = fore[self.Source]
        model.birth(n=self.ImN, ti=ti, **self.ImInfo)

    @staticmethod
    def decorate(name, model, **kwargs):
        if 'mod_src' not in kwargs:
            kwargs['mod_src'] = None
        if 'par_src' not in kwargs:
            kwargs['par_src'] = None
        if 'im_info' not in kwargs:
            kwargs['im_info'] = None

        model.Behaviours[name] = Immigration(name, **kwargs)

    def match(self, be_src, ags_src, ags_new, ti):
        self.ImInfo = dict(be_src.ImInfo)
        self.ImN = be_src.ImN

    def __repr__(self):
        opt = self.Name, '{}@{}'.format(self.Model, self.Source), self.ImN
        return 'Immigration({}, From ={}, Value={})'.format(*opt)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.ImN
        return obs
