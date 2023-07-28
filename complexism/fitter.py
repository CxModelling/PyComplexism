from abc import ABCMeta, abstractmethod
from epidag.fitting import BayesianModel
import complexism as cx


class CxFitter(BayesianModel, metaclass=ABCMeta):
    def __init__(self, sm, da, m_sim, t0=0, t1=10, dt=1, m_warm_up=None, t_warm_up=300):
        BayesianModel.__init__(self, sm.BN)
        self.SimCore = sm
        self.Ctrl = da

        self.SimModel = m_sim
        self.StartTime = t0
        self.EndTime = t1
        self.DiffTime = dt

        self.WarmUpModel = m_warm_up
        self.WarmUpPeriod = t_warm_up

        self.Save = True
        self.Temp = ()
        self.Saved = dict()
        self.Index = 1

    def sample_prior(self):
        prior = self.SimCore.generate('Sim{:06d}'.format(self.Index))
        self.Index += 1
        return prior

    def _sample_y0(self):
        return self.Ctrl.get_y0s(self.WarmUpModel if self.WarmUpModel else self.SimModel)

    @abstractmethod
    def _check_mid_term(self, y0, p):
        return True

    @abstractmethod
    def _transport_y0(self, model):
        pass

    @abstractmethod
    def _calculate_likelihood(self, p, out):
        pass

    def simulate(self, p, y0):
        model = self.Ctrl.generate_model('Y', self.SimModel, pc=p)
        return cx.simulate(model, y0, self.StartTime, self.EndTime, self.DiffTime, log=False)

    def warm_up(self, p):
        y0 = self._sample_y0()

        if not self.WarmUpModel:
            return y0

        model = self.Ctrl.generate_model('Fit', self.WarmUpModel, pc=p)

        if isinstance(self.WarmUpPeriod, tuple):
            t0, t1 = self.WarmUpPeriod
        else:
            t0, t1 = 0, self.WarmUpPeriod

        cx.simulate(model, y0, t0, t1, self.DiffTime, log=False)
        return self._transport_y0(model)

    @property
    def has_exact_likelihood(self):
        return False

    def evaluate_likelihood(self, prior):
        y0 = self.warm_up(prior)
        if not self._check_mid_term(y0, prior):
            return -float('inf')
        out = self.simulate(prior, y0)
        return self._calculate_likelihood(prior, out)


class CxFnFitter(CxFitter):
    def __init__(self, sm, da, m_sim, fn_y0, fn_likelihood, t0=0, t1=10, dt=1,
                 m_warm_up=None, t_warm_up=300,
                 fn_trans_y0=None, fn_check=None):
        CxFitter.__init__(self, sm, da, m_sim, t0, t1, dt, m_warm_up, t_warm_up)
        self.Y0Function = fn_y0
        self.TransportY0Function = fn_trans_y0
        self.MidTermChecker = fn_check
        self.LikelihoodFunction = fn_likelihood

    def _sample_y0(self):
        return self.Y0Function()

    def _transport_y0(self, model):
        return self.TransportY0Function(model)

    def _check_mid_term(self, y0, p):
        return self.MidTermChecker(y0, p)

    def _calculate_likelihood(self, p, out):
        return self.LikelihoodFunction(p, out)
