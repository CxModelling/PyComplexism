__author__ = 'TimeWz667'


class FnODE:
    def __init__(self, func, pars):
        self.Func = func
        self.Pars = pars

    def __call__(self, y, t):
        return self.Func(y, t, self.Pars)

    def __setitem__(self, k, v):
        if k in self.Pars:
            self.Pars[k] = v

    def __getitem__(self, k):
        try:
            return self.Pars[k]
        except IndexError:
            return None

    def __contains__(self, item):
        return item in self.Pars
