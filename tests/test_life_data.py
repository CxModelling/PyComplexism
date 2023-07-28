import unittest
from src.pycx.misc import DemographyLeeCarter
import pandas as pd


class LeeCarterTestCase(unittest.TestCase):
    def setUp(self):
        mat_a = pd.read_csv('../data/LCA/lcA.Age.csv')
        mat_t = pd.read_csv('../data/LCA/LCA.Time.csv')

        mat_bf = pd.read_csv('../data/LCA/BirR.Female.csv')
        mat_bm = pd.read_csv('../data/LCA/BirR.Male.csv')

        mat_af = pd.read_csv('../data/LCA/PopStart.Female.csv')
        mat_am = pd.read_csv('../data/LCA/PopStart.Male.csv')
        mat_af = mat_af.fillna(0)
        mat_am = mat_am.fillna(0)

        lcp = DemographyLeeCarter()

        lcp.load_death_female(mat_a, mat_t, i_year='Year', i_age='Age', i_al='ax_f', i_be='bx_f', i_ka='female')
        lcp.load_death_male(mat_a, mat_t, i_year='Year', i_age='Age', i_al='ax_m', i_be='bx_m', i_ka='male')

        lcp.load_birth_female(mat_bm, i_year='Year', i_rate='br')
        lcp.load_birth_male(mat_bf, i_year='Year', i_rate='br')

        lcp.load_pop_female(mat_af, i_year='Year', ages=range(0, 101))
        lcp.load_pop_male(mat_am, i_year='Year', ages=range(0, 101))

        lcp.complete_loading()
        lcp, lcp.get_death_rate(1990, 'Female', 80), lcp.get_birth_rate(1990)

        self.LCA = lcp

    def test_death_rate(self):
        print(self.LCA.get_death_rate(1990, 'Female', 80))

    def test_birth_rate(self):
        print(self.LCA.get_birth_rate(1990))

    def test_age_structure(self):

        sampler = self.LCA.get_population_sampler(1990)
        print(sampler(4))
        xs = sampler(1000)
        print(sum(x[0] == 'Female' for x in xs))


if __name__ == '__main__':
    unittest.main()
