import matplotlib.pyplot as plt
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

model_name = 'M1'
dc = cx.read_dbp_script(dsc)
Gene = sm.generate()
eve = ss.StSpBreeder('Ag ', 'agent', Gene, dc)
pop = cx.Population(eve)


if __name__ == '__main__':
    model = cx.AgentBasedModel(model_name, Gene, pop)
    model.add_observing_event(pop.Eve.DCore.Transitions['Infect'])

    def f(m, tab, ti):
        tab['Sus'] = m.Population.count(st='Sus')
        tab['Inf'] = m.Population.count(st='Inf')
        tab['Rec'] = m.Population.count(st='Rec')
        tab['Alive'] = m.Population.count(st='Alive')
        tab['Dead'] = m.Population.count(st='Dead')


    model.add_observing_function(f)

    y0 = [
        {'n': 995, 'attributes': {'st': 'Sus'}},
        {'n': 5, 'attributes': {'st': 'Inf'}},
    ]

    output = cx.simulate(model, y0, 0, 10, 1)
    output[['Sus', 'Inf', 'Rec']].plot()
    plt.show()
