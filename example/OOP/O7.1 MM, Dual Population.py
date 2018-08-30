import epidag as dag
import complexism as cx
from complexism.misc import start_counting, stop_counting, get_results
import complexism.agentbased.statespace as ss

__author__ = 'TimeWz667'

director = cx.Director()

director.load_bayes_net('../scripts/pDzAB.txt')
director.load_state_space_model('../scripts/DzAB.txt')

mbp = ss.BlueprintStSpABM('abm')
mbp.set_agent(prefix='Ag', group='agent', dynamics='DzAB')
mbp.set_observations(states=['ab', 'aB', 'Ab', 'AB'])


# Initialise parameters
bn = director.get_bayes_net('pDzAB')

hie = {
    'city': ['abm'],
    'abm': ['agent'],
    'agent': ['TrA', 'TrB', 'TrA_B']
}

sm = dag.as_simulation_core(bn, hie=hie)

# Create a multi-model, and defined initial value
model_name = 'MultiModel'

pc = sm.generate(model_name)

model = cx.MultiModel(model_name, pc)

y0s = cx.BranchY0()
for i in range(1, 3):
    name = 'A{}'.format(i)
    m_abm = mbp.generate(name, pc=pc.breed(name, 'abm'), dc=director.get_state_space_model('DzAB'))
    model.append_child(m_abm, True)
    y0 = cx.LeafY0()
    y0.define({'n': 300, 'attributes': {'st': 'ab'}})
    y0s.append_child(name, y0)


start_counting('MM')
output = cx.simulate(model, y0s, 0, 10, 1)
stop_counting()
print(output)
print()
print(get_results('MM'))
