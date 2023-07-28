import unittest
import pycx as cx
import sims_pars as dag


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

        self.assertSetEqual(set(self.BP.RequiredSamplers), {'TrAB', 'TrBC'})
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
        self.assertTrue(self.BP.add_microstate('A', ['N', 'Y']))
        self.assertFalse(self.BP.add_microstate('A', ['N', 'Y']))
        self.assertTrue(self.BP.add_microstate('B', ['N', 'Y']))

        self.assertTrue(self.BP.add_state('A', A='Y'))
        self.assertFalse(self.BP.add_state('A', A='Y'))
        self.assertTrue(self.BP.add_state('a', A='N'))

        self.BP.add_state('B', B='Y')
        self.BP.add_state('b', B='N')
        self.BP.add_state('ab', A='N', B='N')
        self.BP.add_state('AB', A='Y', B='Y')

        self.BP.add_transition('TrA', 'A', 'exp(0.1)')
        self.BP.add_transition('TrB', 'B')

        self.BP.link_state_transition('a', 'TrA')
        self.BP.link_state_transition('b', 'TrB')

    def test_generate(self):
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

        md_test = self.BP.generate_model(**self.Dists)

        state_ab = md_test['ab']
        state_a = md_test['a']
        state_A = md_test['A']
        self.assertEqual(str(state_ab), 'ab')
        self.assertTrue(state_ab.isa(state_a))
        self.assertTrue(state_a in state_ab)
        self.assertFalse(state_A in state_ab)

        self.assertIn(md_test.Transitions['TrA'], state_ab.next_transitions())
        self.assertIn(md_test.Transitions['TrB'], state_ab.next_transitions())

        t0 = 0
        evt = state_ab.next_event(t0)
        state = state_ab
        t1 = evt.Time
        state = state.execute(evt)
        self.assertGreater(t1, t0)

        evt = state.next_event(t1)
        t0, t1 = t1, evt.Time
        state = state.execute(evt)
        self.assertGreater(t1, t0)

        self.assertEqual(state, md_test['AB'])


if __name__ == '__main__':
    unittest.main()
