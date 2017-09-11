from numpy.random import random, choice
import numpy as np
from scipy import interpolate
import pandas as pd


class CategoricalRV:
    """
    Generate Categorical data with respect to a specific probability distribution.
    """

    def __init__(self, xp):
        """

        :param xp: a dictionary with keys of category names and values of probabilities.
        """
        self.xp = xp
        self.cat = [k for k in xp.keys()]
        self.p = np.array(list(xp.values()))
        self.p = self.p / self.p.sum()

    def __call__(self):
        return self.rvs(1)[0]

    def rvs(self, n=1):
        return choice(self.cat, n, p=self.p)[0]

    def get_xs(self):
        return self.xp


class LeeCarterProcess:
    def __init__(self, path_lct, path_lcx):
        lct = pd.DataFrame.from_csv(path_lct, index_col=False, parse_dates=False)
        lcx = pd.DataFrame.from_csv(path_lcx, index_col=False, parse_dates=False)

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
            return f(random(n) * ps[age]) - age

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
        return 'Male' if random() < self.ProbMale else 'Female'

    def sample_time_to_death(self, info, ti, n=1):
        age = info['Age']
        bir_yr = np.floor(ti) - age
        sex = info['Sex']
        try:
            fn = self.Used['{}{}'.format(sex, bir_yr)]
        except KeyError:
            fn = self.LeeCarter.get_func_time_to_death(sex, bir_yr)
            self.Used['{}{}'.format(sex, bir_yr)] = func
        return fn(age, n)


class LinearCombination:
    def __init__(self, intercept=0, default=0, ):
        self.Coefficients = dict()
        self.TransFunc = None
        self.Intercept = intercept
        self.Default = default

    def __setitem__(self, cov, coe):
        self.Coefficients[cov] = coe

    def append(self, cov, coe=1):
        self.Coefficients[cov] = coe

    def update(self, cos):
        self.Coefficients.update(cos)

    def calculate(self, values):
        y = sum([coe*(values[cov] if cov in values else self.Default)
                 for cov, coe in self.Coefficients.items()])
        y += self.Intercept
        try:
            return self.TransFunc(y)
        except TypeError:
            return y

    def __repr__(self):
        fn = ['{}{}{}'.format('+' if v >= 0 else '', v, k) for k, v in self.Coefficients.items()]
        fn.append('{}{}'.format('+' if self.Intercept >= 0 else '', self.Intercept))
        fn = ' '.join(fn)

        return fn


if __name__ == '__main__':
    crv1 = CategoricalRV({'A': 3, 'B': 4, 'C': 7})
    print(crv1())
    print(crv1.rvs(5))

    pth_lct = '../Data/lcat.csv'
    pth_lcx = '../Data/lcax.csv'

    LCP = LeeCarterProcess(pth_lct, pth_lcx)

    func = LCP.get_func_time_to_death('Female', 1990)
    print(func(age=26, n=10000).mean())
