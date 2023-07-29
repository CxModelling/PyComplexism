import numpy as np
import numpy.random as rd
from scipy import interpolate
import pandas as pd
import epidag.data as dat

__author__ = 'TimeWz667'
__all__ = ['DemographyLeeCarter']


class LeeCarterProcess:
    def __init__(self, path_lct, path_lcx):
        lct = pd.read_csv(path_lct, index_col=False, parse_dates=False)
        lcx = pd.read_csv(path_lcx, index_col=False, parse_dates=False)

        self.Kt = dict()
        self.Kt['Male'] = {row['Year']: row['male'] for k, row in lct.iterrows()}
        self.Kt['Female'] = {row['Year']: row['female'] for k, row in lct.iterrows()}
        self.Ax = {'Male': lcx.ax_m, 'Female': lcx.ax_f}
        self.Bx = {'Male': lcx.bx_m, 'Female': lcx.bx_f}

        self.Bound = lct.Year.min(), lct.Year.max()

    def get_death_rate(self, age, sex, yr):
        yr = min(max(yr, self.Bound[0]), self.Bound[1])
        return np.exp(self.Ax[sex][age] + self.Bx[sex][age] * self.Kt[sex][yr])

    def get_cohort(self, sex, birth_yr):
        return np.array([self.get_death_rate(age, sex, birth_yr + age) for age in range(100)])

    def get_func_time_to_death(self, sex, birth_yr):
        ps = self.get_cohort(sex, birth_yr)
        ps = np.exp(-ps)
        ps = ps.cumprod()
        f = interpolate.interp1d(ps, range(100), bounds_error=False, fill_value=(99, 0))

        def func(age=0, n=1):
            return f(rd.random(n) * ps[age]) - age

        return func


class Demography:
    def __init__(self, yr, path_lct, path_lcx, path_nb, path_agestr, rmf=1.05):
        self.StartYear = yr
        self.LeeCarter = LeeCarterProcess(path_lct, path_lcx)
        self.AgeStr = pd.DataFrame.from_csv(path_agestr, index_col=False, parse_dates=False)
        self.NBirth = pd.DataFrame.from_csv(path_nb, index_col=False, parse_dates=False)
        self.ProbMale = rmf / (1 + rmf)
        self.IniPop = self.AgeStr.Weight.sum()
        self.Used = dict()

    def get_fill_age_sex(self):
        wt = self.AgeStr.Weight
        tab = self.AgeStr.iloc[:, 0:self.AgeStr.shape[1] - 1]

        def func(info):
            if 'Age' in info:
                if 'Sex' not in info:
                    info['Sex'] = self.sample_sex()
            else:
                vs = tab.sample(weights=wt).iloc[0, :]
                info.update(vs)
            return info

        return func

    def get_n_birth(self, yr, p0):
        if yr < self.StartYear:
            return 0
        try:
            return float(self.NBirth.N[self.NBirth.Year == yr] * p0 / self.IniPop)
        except TypeError:
            return float(self.NBirth.iloc[-1, 1] * p0 / self.IniPop)

    def sample_sex(self):
        return 'Male' if rd.random() < self.ProbMale else 'Female'

    def sample_time_to_death(self, info, ti, n=1):
        age = info['Age']
        bir_yr = np.floor(ti) - age
        sex = info['Sex']
        try:
            fn = self.Used['{}{}'.format(sex, bir_yr)]
        except KeyError:
            fn = self.LeeCarter.get_func_time_to_death(sex, bir_yr)
            self.Used['{}{}'.format(sex, bir_yr)] = fn
        return fn(age, n)



