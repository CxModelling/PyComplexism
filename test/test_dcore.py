import unittest
import complexism as cx
import epidag as dag


class CTMCTestCase(unittest.TestCase):
    def setUp(self):
        self.BP = cx.BlueprintCTMC('Test')
        self.Dists = {
            'TrAB': dag.parse_distribution('exp(0.02)'),
            'TrBC': dag.parse_distribution('gamma(1, 0.1)')
        }

    def test_add_state_transition(self):
        self.assertTrue(self.BP.add_state('A'))
        self.assertListEqual(self.BP.States, ['A'])
        self.assertFalse(self.BP.add_state('A'))

        self.assertTrue(self.BP.add_transition('TrAB', 'B'))
        self.assertListEqual(self.BP.States, ['A', 'B'])

        self.assertFalse(self.BP.add_transition('TrAB', 'B'))
        self.assertTrue(self.BP.add_transition('TrBC', 'C'))
        self.assertTrue(self.BP.add_transition('TrCA', 'A', 'exp(0.1)'))
        self.assertEqual(len(self.BP.Transitions), 3)

        self.assertSetEqual(set(self.BP.find_required_distributions()), {'TrAB', 'TrBC'})
        self.assertTrue(self.BP.link_state_transition('A', 'TrAB'))
        self.assertTrue(self.BP.link_state_transition('B', 'TrBC'))
        self.assertTrue(self.BP.link_state_transition('C', 'TrCA'))

    def test_generate(self):
        self.BP.add_transition('TrAB', 'B')
        self.BP.add_transition('TrBC', 'C')
        self.BP.add_transition('TrCA', 'A', 'exp(0.1)')

        self.BP.link_state_transition('A', 'TrAB')
        self.BP.link_state_transition('B', 'TrBC')
        self.BP.link_state_transition('C', 'TrCA')

        # self.assertRaises(self.BP.generate_model(), KeyError)
        dc = self.BP.generate_model(**self.Dists)
        sta = dc['A']
        self.assertEqual(sta.Name, 'A')
        self.assertIn(dc.Transitions['TrAB'], sta.next_transitions())
        eva = sta.next_event()
        self.assertTrue(eva.Time > 0)
        stb = sta.execute(eva)
        self.assertEqual(stb, dc['B'])

        evb = stb.next_event(10000)
        self.assertTrue(evb.Time > 10000)



class CTBNTestCase(unittest.TestCase):
    def setUp(self):
        self.BP = cx.BlueprintCTBN('Test')
        self.Dists = {
            'TrB': dag.parse_distribution('gamma(1, 0.1)')
        }

    def test_add_state_transition(self):
        self.BP.add_microstate('A', ['N', 'Y'])
        self.BP.add_microstate('B', ['N', 'Y'])

        self.BP.add_state('A', A='Y')
        self.BP.add_state('a', A='N')
        self.BP.add_state('B', B='Y')
        self.BP.add_state('b', B='N')
        self.BP.add_state('ab', A='N', B='N')
        self.BP.add_state('AB', A='Y', B='Y')

        self.BP.add_transition('TrA', 'A', 'exp(0.1)')
        self.BP.add_transition('TrB', 'B')

        self.BP.link_state_transition('a', 'TrA')
        self.BP.link_state_transition('b', 'TrB')


        self.assertTrue(self.BP.add_state('A'))
        self.assertListEqual(self.BP.States, ['A'])
        self.assertFalse(self.BP.add_state('A'))

        self.assertTrue(self.BP.add_transition('TrAB', 'B'))
        self.assertListEqual(self.BP.States, ['A', 'B'])

        self.assertFalse(self.BP.add_transition('TrAB', 'B'))
        self.assertTrue(self.BP.add_transition('TrBC', 'C'))
        self.assertTrue(self.BP.add_transition('TrCA', 'A', 'exp(0.1)'))
        self.assertEqual(len(self.BP.Transitions), 3)

        self.assertTrue(self.BP.link_state_transition('A', 'TrAB'))
        self.assertTrue(self.BP.link_state_transition('B', 'TrBC'))
        self.assertTrue(self.BP.link_state_transition('C', 'TrCA'))

    def test_generate(self):
        self.BP.add_transition('TrAB', 'B')
        self.BP.add_transition('TrBC', 'C')
        self.BP.add_transition('TrCA', 'A', 'exp(0.1)')

        self.BP.link_state_transition('A', 'TrAB')
        self.BP.link_state_transition('B', 'TrBC')
        self.BP.link_state_transition('C', 'TrCA')

        # self.assertRaises(self.BP.generate_model(), KeyError)
        dc = self.BP.generate_model(**self.Dists)
        sta = dc['A']
        self.assertEqual(sta.Name, 'A')
        self.assertIn(dc.Transitions['TrAB'], sta.next_transitions())
        eva = sta.next_event()
        self.assertTrue(eva.Time > 0)
        stb = sta.execute(eva)
        self.assertEqual(stb, dc['B'])

        evb = stb.next_event(10000)
        self.assertTrue(evb.Time > 10000)



if __name__ == '__main__':
    unittest.main()
