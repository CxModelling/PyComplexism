import unittest
import complexism as cx
import epidag as dag


psc = """
    PCore pSIR {
        beta = 0.4
        gamma = 0.5
        Infect ~ exp(beta)
        Recov ~ exp(0.5)
        Die ~ exp(0.02)
    }
    """

dsc = """
CTBN SIR {
    life[Alive | Dead]
    sir[S | I | R]

    Alive{life:Alive}
    Dead{life:Dead}
    Inf{life:Alive, sir:I}
    Rec{life:Alive, sir:R}
    Sus{life:Alive, sir:S}

    Die -> Dead # from transition Die to state Dead by distribution Die
    Sus -- Infect -> Inf
    Inf -- Recov -> Rec

    Alive -- Die # from state Alive to transition Die
}
"""

bn = cx.read_pc(psc)
sm = dag.as_simulation_core(bn,
                            hie={'city': ['agent'],
                                 'agent': ['Recov', 'Die', 'Infect']})

pc = sm.generate()

dc = cx.read_dc(dsc)

Name = 'M1'
proto = pc.breed('proto_agent_{}'.format(Name), 'agent')


class StateSpaceAgentTestCase(unittest.TestCase):
    def setUp(self):
        self.DC = dc.generate_model(Name, **pc.get_child_actors('agent'))
        self.Agent = cx.StSpAgent('Helen', self.DC['Sus'])

    def test_creation(self):
        self.Agent.initialise(time=0)
        nxt = self.Agent.Next

        self.assertIn(nxt.Todo, [self.DC.Transitions[tr] for tr in ['Infect', 'Die']])
        self.assertGreater(nxt.Time, 0)

        self.assertIn(self.DC['Alive'], self.Agent)

    def test_transition(self):
        self.Agent.State = self.DC['Sus']
        self.Agent.initialise(time=100)
        nxt = self.Agent.Next
        nxt.Todo = self.DC.Transitions['Infect']

        self.Agent.execute_event()
        self.assertEqual(self.Agent.State, self.DC['Inf'])
        self.Agent.Transitions[self.DC.Transitions['Die']] = 1000
        self.Agent.drop_next()
        self.Agent.update_time(nxt.Time)
        self.assertEqual(self.Agent.Transitions[self.DC.Transitions['Die']], 1000)

        nxt = self.Agent.Next

        self.assertEqual(nxt.Todo, self.DC.Transitions['Recov'])
        self.Agent.execute_event()
        self.assertEqual(self.Agent.State, self.DC['Rec'])
        self.Agent.drop_next()
        self.Agent.update_time(nxt.Time)

        nxt = self.Agent.Next
        self.assertEqual(nxt.Time, 1000)


if __name__ == '__main__':
    unittest.main()
