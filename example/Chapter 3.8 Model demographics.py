import complexism as cx
import complexism.agentbased.statespace as stsp
import epidag as dag


psc = """
PCore pBAD {
    dr = 0.1
    Die ~ exp(dr)
    ToM ~ k(3)
    ToO ~ k(3)
}
"""

dsc = """
CTBN BAD {
    life[Alive | Dead]
    age[Y | M | O]

    Alive{life:Alive}
    Dead{life:Dead}
    Young{life:Alive, age:Y}
    Middle{life:Alive, age:M}
    Old{life:Alive, age:O}

    Alive -- Die -> Dead # from transition Die to state Dead by distribution Die
    Young -- ToM -> Middle
    Middle -- ToO -> Old
}
"""

bn = cx.read_pc(psc)
sm = dag.as_simulation_core(bn,
                            hie={'city': ['agent'],
                                 'agent': ['Die', 'ToM', 'ToO']})

model_name = 'M1'
dc = cx.read_dc(dsc)
Gene = sm.generate()
eve = stsp.StSpBreeder('Ag ', 'agent', Gene, dc)
pop = cx.Population(eve)


if __name__ == '__main__':
    model = cx.StSpAgentBasedModel(model_name, Gene, pop)
    ss = model.Population.Eve.DCore
    stsp.Reincarnation.decorate('Life', model=model, s_death='Dead', s_birth='Young')

    for tr in ['Die', 'ToM', 'ToO']:
        model.add_observing_transition(tr)

    for st in ['Young', 'Middle', 'Old', 'Alive', 'Dead']:
        model.add_observing_state(st)

    y0 = [
        {'n': 30, 'attributes': {'st': 'Young'}},
        {'n': 30, 'attributes': {'st': 'Middle'}},
        {'n': 30, 'attributes': {'st': 'Old'}},
    ]

    print(cx.simulate(model, y0, 0, 10, 1))
