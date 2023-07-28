import unittest
from mcore.impchecker import *
from element.scheduler import Disclosure


class CheckerCase(unittest.TestCase):
    def test_is_checker(self):
        truthy = Disclosure('Message', 'Mr. Right', 'Here')
        falsy = Disclosure('Massage', 'Mr. Wrong', 'There')

        checker = IsChecker('Message')
        self.assertTrue(checker(truthy))
        self.assertFalse(checker(falsy))

        checker = IsChecker.from_json(checker.to_json())
        self.assertTrue(checker(truthy))
        self.assertFalse(checker(falsy))

    def test_start_with_checker(self):
        truthy = Disclosure('Go to somewhere', 'Mr. Right', 'Here')
        falsy = Disclosure('Do something', 'Mr. Wrong', 'There')

        checker = StartsWithChecker('Go to')
        self.assertTrue(checker(truthy))
        self.assertFalse(checker(falsy))

        checker = StartsWithChecker.from_json(checker.to_json())
        self.assertTrue(checker(truthy))
        self.assertFalse(checker(falsy))

    def test_inclusion_checker(self):
        truthy = Disclosure('Read', 'Mr. Right', 'Here')
        falsy = Disclosure('Study', 'Mr. Wrong', 'There')

        checker = InclusionChecker(['Play', 'Read', 'Walk'])
        self.assertTrue(checker(truthy))
        self.assertFalse(checker(falsy))

        checker = InclusionChecker.from_json(checker.to_json())
        self.assertTrue(checker(truthy))
        self.assertFalse(checker(falsy))

    def test_who_start_with_checker(self):
        truthy = Disclosure('Go to somewhere', 'Mr. Right', 'Here')
        falsy_a = Disclosure('Go to somewhere', 'Mr. Wrong', 'There')
        falsy_b = Disclosure('Do something', 'Mr. Right', 'There')
        falsy_c = Disclosure('Do something', 'Mr. Wrong', 'There')

        checker = WhoStartWithChecker('Mr. Right', 'Go to')
        self.assertTrue(checker(truthy))
        self.assertFalse(checker(falsy_a))
        self.assertFalse(checker(falsy_b))
        self.assertFalse(checker(falsy_c))

        checker = WhoStartWithChecker.from_json(checker.to_json())
        self.assertTrue(checker(truthy))
        self.assertFalse(checker(falsy_a))
        self.assertFalse(checker(falsy_b))
        self.assertFalse(checker(falsy_c))


if __name__ == '__main__':
    unittest.main()
