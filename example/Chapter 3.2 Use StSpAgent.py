import complexism as cx
import complexism.agentbased.statespace as ss
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

bn = cx.read_bn_script(psc)
sm = dag.as_simulation_core(bn,
                            hie={'city': ['agent'],
                                 'agent': ['Recov', 'Die', 'Infect']})

dc = cx.read_dbp_script(dsc)
Gene = sm.generate()
proto = Gene.get_prototype('agent')
SIR = dc.generate_model('M1', **proto.get_samplers())


def step(agent):
    evt = agent.Next
    agent.execute_event()
    agent.drop_next()
    agent.update_time(evt.Time)
    return evt.Time


if __name__ == '__main__':
    ag = ss.StSpAgent('Helen', SIR['Sus'])
    ag.initialise(0)

    print('Agent is a {}'.format(ag.State))
    ti = 0
    while ti < 100:
        ti = step(ag)
        print('Time:', ti)
        print('Agent is a {}'.format(ag.State))
