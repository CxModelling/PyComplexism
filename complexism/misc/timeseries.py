import numpy as np
import numpy.random as rd
from scipy import interpolate
import pandas as pd
import epidag.data as dat

__author__ = 'TimeWz667'


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


class DemographySimplified:
    def __init__(self, path_life, adj=1):
        demo = pd.DataFrame.from_csv(path_life)
        yrs = np.array(demo.Year)
        ns = np.array(demo.Pop) * adj
        dr = np.array(demo.DeathRate)
        br = np.array(demo.BirthRate)
        self.StartYear = yrs[0]

        self.RateDeath = interpolate.interp1d(yrs, dr, bounds_error=False, fill_value=(dr[0], dr[-1]))
        self.Num = interpolate.interp1d(yrs, ns, bounds_error=False, fill_value=(ns[0], ns[-1]))
        self.RateBirth = interpolate.interp1d(yrs, br, bounds_error=False, fill_value=(br[0], br[-1]))


class StepFn:
    def __init__(self, ts, ys):
        self.Ts = ts
        self.Ys = ys

    def __call__(self, ti):
        for t, y in zip(self.Ts, self.Ys):
            if t > ti:
                return y
        return self.Ys[-1]

    def __repr__(self):
        s = ['{}({})'.format(y, t) for y, t in zip(self.Ys[1:], self.Ts)]
        return self.Ys[0] + '-' + '-'.join(s)

    def to_json(self):
        return {'Fn': 'Step', 'Ts': self.Ts, 'Ys': self.Ys}


class DemographyLeeCarter:
    def __init__(self):
        self.InputComplete = False
        self.Death = {
            'Female': None,
            'Male': None,
        }
        self.Birth = {
            'Female': None,
            'Male': None,
        }
        self.AgeStr = {
            'Female': None,
            'Male': None
        }
        self.YearStart = -float('inf')
        self.YearEnd = float('inf')
        self.Ages = None

    def load_death_female(self, df_a, df_t, i_year='Year', i_age='Age', i_al='ax_m', i_be='bx_m', i_ka='female'):
        """
        Load death rate data of female with Lee Carter parametrisation
        :param df_a: data with alpha and beta terms
        :type df_a: pd.DataFrame
        :param df_t: data with kappa term
        :type df_t: pd.DataFrame
        :param i_year: column name of year
        :type i_year: str
        :param i_age: column name of age
        :type i_age: str
        :param i_al: column name of alpha series (age)
        :type i_al: str
        :param i_be: column name of beta series (age)
        :type i_be: str
        :param i_ka: column name of kappa series (time)
        :type i_ka: str
        """
        if not self.InputComplete:
            self.Death['Female'] = dat.LeeCarter(df_t, df_a, i_time=i_year, i_age=i_age, i_al=i_al, i_be=i_be, i_ka=i_ka)
            self.YearStart = max(self.YearStart, df_t[i_year].min())
            self.YearEnd = min(self.YearEnd, df_t[i_year].max())

    def load_death_male(self, df_a, df_t, i_year='Year', i_age='Age', i_al='ax_m', i_be='bx_m', i_ka='male'):
        """
        Load death rate data of male with Lee Carter parametrisation
        :param df_a: data with alpha and beta terms
        :type df_a: pd.DataFrame
        :param df_t: data with kappa term
        :type df_t: pd.DataFrame
        :param i_year: column name of year
        :type i_year: str
        :param i_age: column name of age
        :type i_age: str
        :param i_al: column name of alpha series (age)
        :type i_al: str
        :param i_be: column name of beta series (age)
        :type i_be: str
        :param i_ka: column name of kappa series (time)
        :type i_ka: str
        """
        if not self.InputComplete:
            self.Death['Male'] = dat.LeeCarter(df_t, df_a, i_time=i_year, i_age=i_age, i_al=i_al, i_be=i_be, i_ka=i_ka)
            self.YearStart = max(self.YearStart, df_t[i_year].min())
            self.YearEnd = min(self.YearEnd, df_t[i_year].max())

    def load_birth_female(self, df, i_year='Year', i_rate='br'):
        """
        Load birth rate data of new born females
        :param df: data with alpha and beta terms
        :type df: pd.DataFrame
        :param i_year: column name of year
        :type i_year: str
        :param i_rate: column name of birth rate
        :type i_rate: str
        """
        if not self.InputComplete:
            self.Birth['Female'] = dat.TimeSeries(df, i_year, i_rate)
            self.YearStart = max(self.YearStart, df[i_year].min())
            self.YearEnd = min(self.YearEnd, df[i_year].max())

    def load_birth_male(self, df, i_year='Year', i_rate='br'):
        """
        Load birth rate data of new born males
        :param df: data with alpha and beta terms
        :type df: pd.DataFrame
        :param i_year: column name of year
        :type i_year: str
        :param i_rate: column name of birth rate
        :type i_rate: str
        """
        if not self.InputComplete:
            self.Birth['Male'] = dat.TimeSeries(df, i_year, i_rate)
            self.YearStart = max(self.YearStart, df[i_year].min())
            self.YearEnd = min(self.YearEnd, df[i_year].max())

    def load_pop_female(self, df, i_year='Year', prefix='', ages=range(0, 101)):
        """
        Load population size of females
        :param df: data with alpha and beta terms
        :type df: pd.DataFrame
        :param prefix: prefix column name for ages
        :type prefix: str
        :param ages: age groups or ages
        :type i_rate: list
        """
        if not self.InputComplete:
            self.Ages = ages = list(ages)
            indices = ['{}{}'.format(prefix, i) for i in ages]
            years = df[i_year]
            tables = dict()
            for _, row in df.iterrows():
                yr = row[i_year]
                d = {a: row[i] for a, i in zip(ages, indices)}
                tables[yr] = pd.Series(d)
            self.AgeStr['Female'] = tables
            self.YearStart = max(self.YearStart, min(years))
            self.YearEnd = min(self.YearEnd, max(years))

    def load_pop_male(self, df, i_year, prefix='', ages=range(0, 101)):
        """
        Load population size of males
        :param df: data with alpha and beta terms
        :type df: pd.DataFrame
        :param prefix: prefix column name for ages
        :type prefix: str
        :param ages: age groups or ages
        :type i_rate: list
        """
        if not self.InputComplete:
            self.Ages = ages = list(ages)
            indices = ['{}{}'.format(prefix, i) for i in ages]
            years = df[i_year]
            tables = dict()
            for _, row in df.iterrows():
                yr = row[i_year]
                d = {a: row[i] for a, i in zip(ages, indices)}
                tables[yr] = pd.Series(d)
            self.AgeStr['Male'] = tables
            self.YearStart = max(self.YearStart, min(years))
            self.YearEnd = min(self.YearEnd, max(years))

    def complete_loading(self):
        """
        Complete the data loading and freeze all the data
        """
        try:
            assert self.Death['Female'] is not None
            assert self.Death['Male'] is not None
            assert self.Birth['Female'] is not None
            assert self.Birth['Male'] is not None
            assert self.AgeStr['Female'] is not None
            assert self.AgeStr['Male'] is not None
        except AssertionError as e:
            raise e
        else:
            self.InputComplete = True

    def get_death_rate(self, year, sex=None, age=None):
        """
        Find the death rates given a single year
        :param year: year of request
        :param sex: sex in ['Female', 'Male']
        :param age: age with respect to age structure data
        :return: death rate value if sex and age specified. Otherwise dict
        """
        assert self.InputComplete
        year = int(year)
        assert year >= self.YearStart
        assert year <= self.YearEnd

        if sex:
            dr = self.Death[sex](year)
            try:
                return dr[age]
            except KeyError:
                return dr
        else:
            return {
                'Female': self.Death['Female'](year),
                'Male': self.Death['Male'](year)
            }

    def get_birth_rate(self, year, sex=None):
        """
        Find the birth rates given a single year
        :param year: year of request
        :param sex: sex in ['Female', 'Male']
        :return: birth rate value if sex specified. Otherwise dict
        """
        assert self.InputComplete
        year = int(year)
        assert year >= self.YearStart
        assert year <= self.YearEnd

        tab_f = self.AgeStr['Female'][year]
        tab_m = self.AgeStr['Male'][year]

        n_f, n_m = tab_f.sum(), tab_m.sum()
        n_all = n_f + n_m

        if sex == 'Female':
            return self.Birth['Female'](year) * n_f / n_all
        elif sex == 'Male':
            return self.Birth['Male'](year) * n_m / n_all
        else:
            return {
                'Female': self.Birth['Female'](year) * n_f / n_all,
                'Male': self.Birth['Male'](year) * n_f / n_all
            }

    def get_prob_female_at_birth(self, year):
        brs = self.get_birth_rate(year)
        return brs['Female'] / (brs['Female'] + brs['Male'])

    def get_population(self, year):
        """
        Find the population size given a single year
        :param year: year of request
        :return: dict(sex->age structure)
        """
        assert self.InputComplete
        year = int(year)
        assert year >= self.YearStart
        assert year <= self.YearEnd

        return {
            'Female': self.AgeStr['Female'][year],
            'Male': self.AgeStr['Male'][year]
        }

    def get_population_sampler(self, year):
        """
        Get a sampler for sampling population given a year
        :param year: year of request
        :return: sampler fn(n=1)
        """
        assert self.InputComplete
        year = int(year)
        assert year >= self.YearStart
        assert year <= self.YearEnd

        tab_f = self.AgeStr['Female'][year]
        tab_m = self.AgeStr['Male'][year]

        n_all = tab_f.sum() + tab_m.sum()
        tab_f = tab_f / n_all
        tab_m = tab_m / n_all
        pr = list(tab_f) + list(tab_m)
        atr = [('Female', a) for a in self.Ages] + [('Male', a) for a in self.Ages]

        def fn(n=1):
            if n is 1:
                sam = rd.choice(range(len(pr)), 1, p=pr)
                return atr[sam[0]]
            else:
                sam = rd.choice(range(len(pr)), n, p=pr)
                return [atr[i] for i in sam]

        return fn

    def __str__(self):
        return 'Life dataset from {} to {}'.format(self.YearStart, self.YearEnd)

    __repr__ = __str__
