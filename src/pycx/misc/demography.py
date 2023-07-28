from abc import ABCMeta, abstractmethod
import functools
import numpy.random as rd
import pandas as pd
import epidag.data as dat

__author__ = 'TimeWz667'
__all__ = ['AbsDemography', 'DemographyTotal', 'DemographySex', 'DemographyLeeCarter']


def check_year(fn):
    @functools.wraps(fn)
    def wrp(this, year, **kwargs):
        assert this.FullyInputted, 'Data have not loaded'

        year = int(year)

        if this.SoftMode:
            year = min(max(year, this.YearEnd), this.YearStart)
        else:
            assert year >= this.YearStart, 'Missed data in {}'.format(year)
            assert year <= this.YearEnd, 'Missed data in {}'.format(year)
        return fn(this, year=year, **kwargs)
    return wrp


class AbsDemography(metaclass=ABCMeta):
    def __init__(self):
        self.YearStart = -float('inf')
        self.YearEnd = float('inf')
        self.FullyInputted = False
        self.SoftMode = False

    @abstractmethod
    def complete_loading(self):
        pass

    def on_soft_mode(self):
        self.SoftMode = True

    def on_hard_mode(self):
        self.SoftMode = False

    @abstractmethod
    def get_death_rate(self, year, **kwargs):
        pass

    @abstractmethod
    def get_birth_rate(self, year, **kwargs):
        pass

    @abstractmethod
    def get_migration_rate(self, year, **kwargs):
        pass

    @abstractmethod
    def get_population(self, year, **kwargs):
        pass

    @abstractmethod
    def get_population_sampler(self, year, **kwargs):
        pass

    def __str__(self):
        return 'Demographic dataset [{}, {}]'.format(self.YearStart, self.YearEnd)

    __repr__ = __str__


class DemographyTotal(AbsDemography):
    def __init__(self):
        AbsDemography.__init__(self)
        self.Death = None
        self.Birth = None
        self.Migration = None
        self.Population = None

        self.CurrentDeath = (0, None)
        self.CurrentBirth = (0, None)
        self.CurrentMigration = (0, None)
        self.CurrentPopulation = (0, None)

    def load_death_data(self, df, i_year, i_death):
        if not self.FullyInputted:
            self.Death = dat.TimeSeries(df, i_year, i_death)

            self.YearStart = max(self.YearStart, df[i_year].min())
            self.YearEnd = min(self.YearEnd, df[i_year].max())

    def load_birth_data(self, df, i_year, i_birth):
        if not self.FullyInputted:
            self.Birth = dat.TimeSeries(df, i_year, i_birth)

            self.YearStart = max(self.YearStart, df[i_year].min())
            self.YearEnd = min(self.YearEnd, df[i_year].max())

    def load_migration_data(self, df, i_year, i_mig):
        if not self.FullyInputted:
            self.Migration = dat.TimeSeries(df, i_year, i_mig)

            self.YearStart = max(self.YearStart, df[i_year].min())
            self.YearEnd = min(self.YearEnd, df[i_year].max())

    def load_population_data(self, df, i_year, i_pop):
        if not self.FullyInputted:
            self.Population = dat.TimeSeries(df, i_year, i_pop)

            self.YearStart = max(self.YearStart, df[i_year].min())
            self.YearEnd = min(self.YearEnd, df[i_year].max())

    def complete_loading(self):
        """
        Complete the data loading and freeze all the data
        """
        try:
            assert self.Death is not None
            assert self.Birth is not None
            assert self.Migration is not None
            assert self.Population is not None
        except AssertionError as e:
            raise e
        else:
            self.FullyInputted = True

    @check_year
    def get_death_rate(self, year):
        if self.CurrentDeath[0] is not year:
            self.CurrentDeath = year, self.Death(year)
        return self.CurrentDeath[1]

    @check_year
    def get_birth_rate(self, year, sex=None):
        if self.CurrentBirth[0] is not year:
            self.CurrentBirth = year, self.Birth(year)
        return self.CurrentBirth[1]

    @check_year
    def get_migration_rate(self, year, sex=None):
        if self.CurrentMigration[0] is not year:
            self.CurrentMigration = year, self.Migration(year)
        return self.CurrentMigration[1]

    @check_year
    def get_population(self, year, sex=None):
        if self.CurrentPopulation[0] is not year:
            self.CurrentPopulation = year, self.Population(year)
        return self.CurrentPopulation[1]

    @check_year
    def get_population_sampler(self, year, **kwargs):
        """
        Get a sampler for sampling population given a year
        :param year: year of request
        :return: sampler fn(n=1)
        """
        pass

    def __str__(self):
        return 'Total Demography, [{}, {}], Birth, Death, Migration'.format(self.YearStart, self.YearEnd)

    __repr__ = __str__


class DemographySex(AbsDemography):
    def __init__(self):
        AbsDemography.__init__(self)
        self.Death = {'Female': None, 'Male': None}
        self.Birth = {'Female': None, 'Male': None}
        self.Migration = {'Female': None, 'Male': None}
        self.Population = {'Female': None, 'Male': None}

        self.CurrentDeath = (0, None)
        self.CurrentBirth = (0, None)
        self.CurrentMigration = (0, None)
        self.CurrentPopulation = (0, None)

    def load_death_data(self, df, i_year, i_f, i_m):
        if not self.FullyInputted:
            self.Death['Female'] = dat.TimeSeries(df, i_year, i_f)
            self.Death['Male'] = dat.TimeSeries(df, i_year, i_m)

            self.YearStart = max(self.YearStart, df[i_year].min())
            self.YearEnd = min(self.YearEnd, df[i_year].max())

    def load_birth_data(self, df, i_year, i_f, i_m):
        if not self.FullyInputted:
            self.Birth['Female'] = dat.TimeSeries(df, i_year, i_f)
            self.Birth['Male'] = dat.TimeSeries(df, i_year, i_m)

            self.YearStart = max(self.YearStart, df[i_year].min())
            self.YearEnd = min(self.YearEnd, df[i_year].max())

    def load_migration_data(self, df, i_year, i_f, i_m):
        if not self.FullyInputted:
            self.Migration['Female'] = dat.TimeSeries(df, i_year, i_f)
            self.Migration['Male'] = dat.TimeSeries(df, i_year, i_m)

            self.YearStart = max(self.YearStart, df[i_year].min())
            self.YearEnd = min(self.YearEnd, df[i_year].max())

    def load_population_data(self, df, i_year, i_f, i_m):
        if not self.FullyInputted:
            self.Population['Female'] = dat.TimeSeries(df, i_year, i_f)
            self.Population['Male'] = dat.TimeSeries(df, i_year, i_m)

            self.YearStart = max(self.YearStart, df[i_year].min())
            self.YearEnd = min(self.YearEnd, df[i_year].max())

    def complete_loading(self):
        """
        Complete the data loading and freeze all the data
        """
        try:
            assert self.Death['Female'] is not None
            assert self.Death['Male'] is not None
            assert self.Birth['Female'] is not None
            assert self.Birth['Male'] is not None
            assert self.Migration['Female'] is not None
            assert self.Migration['Male'] is not None
            assert self.Population['Female'] is not None
            assert self.Population['Male'] is not None
        except AssertionError as e:
            raise e
        else:
            self.FullyInputted = True

    @check_year
    def get_death_rate(self, year, sex=None):
        if sex == 'Female':
            return self.Death['Female'](year)
        elif sex == 'Male':
            return self.Death['Male'](year)
        else:
            if self.CurrentDeath[0] is not year:
                self.CurrentDeath = (year, {
                    'Female': self.Death['Female'](year),
                    'Male': self.Death['Male'](year)
                })

            return self.CurrentDeath[1]

    @check_year
    def get_birth_rate(self, year, sex=None):
        if sex == 'Female':
            return self.Birth['Female'](year)
        elif sex == 'Male':
            return self.Birth['Male'](year)
        else:
            if self.CurrentBirth[0] is not year:
                self.CurrentBirth = (year, {
                    'Female': self.Birth['Female'](year),
                    'Male': self.Birth['Male'](year)
                })

            return self.CurrentBirth[1]

    @check_year
    def get_migration_rate(self, year, sex=None):
        if sex == 'Female':
            return self.Migration['Female'](year)
        elif sex == 'Male':
            return self.Migration['Male'](year)
        else:
            if self.CurrentMigration[0] is not year:
                self.CurrentMigration = (year, {
                    'Female': self.Migration['Female'](year),
                    'Male': self.Migration['Male'](year)
                })

            return self.CurrentMigration[1]

    @check_year
    def get_population(self, year, sex=None):
        if sex == 'Female':
            return self.Population['Female'](year)
        elif sex == 'Male':
            return self.Population['Male'](year)
        else:
            if self.CurrentPopulation[0] is not year:
                self.CurrentPopulation = (year, {
                    'Female': self.Population['Female'](year),
                    'Male': self.Population['Male'](year)
                })

            return self.CurrentPopulation[1]

    @check_year
    def get_population_sampler(self, year, **kwargs):
        """
        Get a sampler for sampling population given a year
        :param year: year of request
        :return: sampler fn(n=1)
        """
        pop_f = self.Population['Female'](year)
        pop_m = self.Population['Male'](year)

        n_all = pop_f + pop_m
        pf = pop_f / n_all
        pm = pop_m / n_all

        def fn(n=1):
            if n is 1:
                sam = rd.choice(['Female', 'Male'], 1, p=[pf, pm])
                return sam[0]
            else:
                sam = rd.choice(['Female', 'Male'], n, p=[pf, pm])
                return sam

        return fn

    def __str__(self):
        return 'Sex-specific demography, [{}, {}], Birth, Death, Migration'.format(self.YearStart, self.YearEnd)

    __repr__ = __str__


class DemographyLeeCarter(AbsDemography):
    def __init__(self):
        AbsDemography.__init__(self)
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
        if not self.FullyInputted:
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
        if not self.FullyInputted:
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
        if not self.FullyInputted:
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
        if not self.FullyInputted:
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
        if not self.FullyInputted:
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
        if not self.FullyInputted:
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
            self.FullyInputted = True

    @check_year
    def get_death_rate(self, year, sex=None, age=None):
        """
        Find the death rates given a single year
        :param year: year of request
        :param sex: sex in ['Female', 'Male']
        :param age: age with respect to age structure data
        :return: death rate value if sex and age specified. Otherwise dict
        """
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

    @check_year
    def get_birth_rate(self, year, sex=None):
        """
        Find the birth rates given a single year
        :param year: year of request
        :param sex: sex in ['Female', 'Male']
        :return: birth rate value if sex specified. Otherwise dict
        """
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

    def get_migration_rate(self, year, **kwargs):
        raise AttributeError('No migration processes')

    @check_year
    def get_prob_female_at_birth(self, year):
        brs = self.get_birth_rate(year)
        return brs['Female'] / (brs['Female'] + brs['Male'])

    @check_year
    def get_population(self, year):
        """
        Find the population size given a single year
        :param year: year of request
        :return: dict(sex->age structure)
        """
        return {
            'Female': self.AgeStr['Female'][year],
            'Male': self.AgeStr['Male'][year]
        }

    @check_year
    def get_population_sampler(self, year, sex=None):
        """
        Get a sampler for sampling population given a year
        :param year: year of request
        :param sex: sex of request none for both
        :return: sampler fn(n=1)
        """
        if sex == 'Female':
            tab_f = self.AgeStr['Female'][year]
            tab_f = tab_f / tab_f.sum()

            pr = list(tab_f)
            ages = list(range(len(pr)))

            def fn(n=1):
                if n is 1:
                    return rd.choice(ages, 1, p=pr)[0]
                else:
                    return rd.choice(ages, n, p=pr)

        elif sex == 'Male':
            tab_m = self.AgeStr['Male'][year]
            tab_m = tab_m / tab_m.sum()

            pr = list(tab_m)
            ages = list(range(len(pr)))

            def fn(n=1):
                if n is 1:
                    return rd.choice(ages, 1, p=pr)[0]
                else:
                    return rd.choice(ages, n, p=pr)
        else:
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
        return 'Age-Sex specific demography [{}, {}], Birth, LeeCarter Death'.format(self.YearStart, self.YearEnd)

    __repr__ = __str__
