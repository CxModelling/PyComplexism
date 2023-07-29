from numpy.random import choice
import numpy as np

__author__ = 'TimeWz667'
__all__ = ['CategoricalRV']


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
