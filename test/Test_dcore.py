import unittest
from complexism import *


class TestCTMC(unittest.TestCase):
    def setUp(self):
        psc = """
            {
                TrAB ~ k(4)
                TrBC ~ gamma(0.01, 100)
                TrCA ~ k(100)
            }
            """
        self.BP = BlueprintCTMC('Test')

    def test_write_bp(self):
        self.BP.add_state('A')
        #self.assertTrue('A' in self.BP.States['A'])

        #self.assertRaises(KeyError, self.BP.add_transition, 'TrAB', 'B', 'trab')
        self.assertEqual(len(self.BP.Transitions), 0)
        self.assertTrue(self.BP.add_transition('TrAB', 'B'))
        self.assertTrue(self.BP.add_transition('TrBC', 'C'))
        self.assertTrue(self.BP.add_transition('TrCA', 'A'))
        self.assertEqual(len(self.BP.Transitions), 3)

        self.assertRaises(KeyError, self.BP.link_state_transition, 'A', 'trAB')
        self.assertTrue(self.BP.link_state_transition('A', 'TrAB'))
        self.assertTrue(self.BP.link_state_transition('B', 'TrBC'))
        self.assertTrue(self.BP.link_state_transition('C', 'TrCA'))


if __name__ == '__main__':
    loader = unittest.TestLoader()

    loader.loadTestsFromTestCase(TestCTMC)
    su = loader.suiteClass()

    unittest.TestSuite([su])
    unittest.main(failfast=True)
