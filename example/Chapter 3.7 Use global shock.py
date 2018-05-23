import complexism as cx
import complexism.agentbased.statespace as ss
import epidag as dag


psc = """
PCore pSIR {
    beta = 1.4
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

model_name = 'M1'
dc = cx.read_dbp_script(dsc)
Gene = sm.generate()
eve = ss.StSpBreeder('Ag ', 'agent', Gene, dc)
pop = cx.Population(eve)


if __name__ == '__main__':
    model = cx.StSpAgentBasedModel(model_name, Gene, pop)
    ss.FDShockFast.decorate('FOI', model=model, s_src='Inf', t_tar='Infect')

    for tr in ['Infect', 'Recov', 'Die']:
        model.add_observing_transition(tr)

    for st in ['Sus', 'Inf', 'Rec', 'Alive', 'Dead']:
        model.add_observing_state(st)

    model.add_observing_behaviour('FOI')

    y0 = [
        {'n': 98, 'attributes': {'st': 'Sus'}},
        {'n': 2, 'attributes': {'st': 'Inf'}},
    ]

    from complexism.misc.counter import *
    start_counting('SIR')
    print(cx.simulate(model, y0, 0, 10, 1))
    stop_counting()
    print(get_results('SIR'))
