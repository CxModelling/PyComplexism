import matplotlib.pyplot as plt
import complexism as cx
import complexism.agentbased.statespace as ss
import epidag as dag


model_name = 'M_SIR'

# Step 1 set a parameter core
bn = cx.read_bn_script(cx.load_txt('../scripts/pSIR.txt'))
sm = dag.as_simulation_core(bn,
                            hie={'city': ['agent'],
                                 'agent': ['Infect', 'Recov', 'Die']})
pc = sm.generate(model_name)


# Step 1- set dynamic cores as agents need
dbp = cx.read_dbp_script(cx.load_txt('../scripts/SIR_BN.txt'))


# Step 2 define at least one type of agent
eve = ss.StSpBreeder('Ag', 'agent', pc, dbp)
pop = cx.Population(eve)


# Step 3 generate a model
model = cx.StSpAgentBasedModel(model_name, pc, pop)


# Step 4 add behaviours to the model
ss.FDShock.decorate('FOI', model, s_src='Inf', t_tar='Infect')
# ss.FDShockFast.decorate('FOI', model=model, s_src='Inf', t_tar='Infect', dt=0.1)
# pc.impulse({'beta': pc['beta']/300})
# ss.DDShock.decorate('FOI', model=model, s_src='Inf', t_tar='Infect')
# ss.DDShockFast.decorate('FOI', model=model, s_src='Inf', t_tar='Infect')


# Step 5 decide outputs
for tr in ['Infect', 'Recov', 'Die']:
    model.add_observing_transition(tr)

for st in ['Sus', 'Inf', 'Rec', 'Alive', 'Dead']:
    model.add_observing_state(st)

model.add_observing_behaviour('FOI')


# Step 6 simulate
y0 = [
    {'n': 490, 'attributes': {'st': 'Sus'}},
    {'n': 10, 'attributes': {'st': 'Inf'}}
]

output = cx.simulate(model, y0, 0, 30, 1)
print(output)


# Step 7 inference, draw figures, and manage outputs
fig, axes = plt.subplots(nrows=3, ncols=1)

output[['Sus', 'Inf', 'Rec']].plot(ax=axes[0])
output[['Recov', 'Infect']].plot(ax=axes[1])
output[['FOI']].plot(ax=axes[2])
plt.show()
