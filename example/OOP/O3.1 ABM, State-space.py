import matplotlib.pyplot as plt
import complexism as cx
import complexism.agentbased.statespace as ss
import epidag as dag


model_name = 'M1'

# Step 1 set a parameter core
bn = cx.read_bn_script(cx.load_txt('../scripts/pDzAB.txt'))
sm = dag.as_simulation_core(bn,
                            hie={'city': ['agent'],
                                 'agent': ['TrA', 'TrB', 'TrA_B']})
pc = sm.generate(model_name)


# Step 1- set dynamic cores as agents need
dbp = cx.read_dbp_script(cx.load_txt('../scripts/DzAB.txt'))


# Step 2 define at least one type of agent
eve = ss.StSpBreeder('Ag ', 'agent', pc, dbp)
pop = cx.Population(eve)


# Step 3 generate a model
model = cx.StSpAgentBasedModel(model_name, pc, pop)


# Step 4 add behaviours to the model


# Step 5 decide outputs
for tr in ['TrA', 'TrB', 'TrA_B']:
    model.add_observing_transition(tr)

for st in ['a', 'b', 'AB']:
    model.add_observing_state(st)


# Step 6 simulate
y0 = [
    {'n': 1e3, 'attributes': {'st': 'ab'}},
]

output = cx.simulate(model, y0, 0, 10, 1)
print(output)


# Step 7 inference, draw figures, and manage outputs
output.plot()
plt.show()
