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

bn = cx.read_pc(psc)
sm = dag.as_simulation_core(bn,
                            hie={'city': ['agent'],
                                 'agent': ['Recov', 'Die', 'Infect']})

dc = cx.read_dc(dsc)
Gene = sm.generate()
proto = Gene.get_prototype('agent')
SIR = dc.generate_model('M1', **proto.get_samplers())


if __name__ == '__main__':
    ag = ss.StSpAgent('Helen', SIR['Sus'])
    model = cx.SingleIndividualABM('M1', ag)
    print(cx.simulate(model, None, 0, 10, 1))
