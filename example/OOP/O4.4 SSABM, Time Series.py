import matplotlib.pyplot as plt
import complexism as cx
import complexism.agentbased.statespace as ss
import epidag as dag


model_name = 'M_BD'

# Step 1 set a parameter core
bn = cx.read_bn_script(cx.load_txt('../scripts/pDzAB.txt'))
sm = dag.as_simulation_core(bn,
                            hie={'city': ['agent'],
                                 'agent': ['TrA', 'TrB', 'TrA_B']})
pc = sm.generate(model_name)


# Step 1- set dynamic cores as agents need
dbp = cx.read_dbp_script(cx.load_txt('../scripts/DzAB.txt'))


# Step 2 define at least one type of agent
eve = ss.StSpBreeder('Ag', 'agent', pc, dbp)
pop = cx.Population(eve)


# Step 3 generate a model
model = cx.StSpAgentBasedModel(model_name, pc, pop)


# Step 4 add behaviours to the model
ss.install_behaviour(model, 'cycle', 'LifeS', s_birth='ab', s_death='AB', rate=0.5, cap=150, dt=1)


# Step 5 decide outputs
# for tr in ['ToM', 'ToO', 'Die']:
#     model.add_observing_transition(tr)

for st in ['A', 'B']:
    model.add_observing_state(st)


# Step 6 simulate
y0 = [
    {'n': 34, 'attributes': {'st': 'ab'}},
    {'n': 33, 'attributes': {'st': 'aB'}},
    {'n': 33, 'attributes': {'st': 'Ab'}}
]


output = cx.simulate(model, y0, 0, 10, 1)
print(output)


# Step 7 inference, draw figures, and manage outputs
output.plot()
plt.show()
