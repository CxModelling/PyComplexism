import complexism as cx
import matplotlib.pyplot as plt


__author__ = 'TimeWz667'

ctrl = cx.Director()
ctrl.load_bayes_net('scripts/pVectorBorne.txt')
ctrl.load_state_space_model('scripts/VectorBorneHuman.txt')
ctrl.load_state_space_model('scripts/VectorBorneVector.txt')

print(ctrl.list_bayes_nets())
print(ctrl.list_state_spaces())


# Human
mbp_h = ctrl.new_sim_model('Human', 'StSpABM')
mbp_h.set_agent(prefix='H', group='human', dynamics='Human')
mbp_h.add_behaviour('Bite', 'ExternalShock', t_tar='Infect_H')
mbp_h.set_observations(states=['S_H', 'I_H', 'R_H'], behaviours=['Bite'])


# Vector
mbp_v = ctrl.new_sim_model('Vector', 'StSpABM')
mbp_v.set_agent(prefix='V', group='vector', dynamics='Vector')
mbp_v.add_behaviour('V2V', 'FDShock', t_tar='Infect_V', s_src='I_V')
mbp_v.add_behaviour('StInf', 'StateTrack', s_src='I_V')
mbp_v.set_observations(states=['S_V', 'I_V'], behaviours=['V2V'])


lyo = ctrl.new_model_layout('VectorBorne')

y0_h = mbp_h.get_y0_proto()
y0_h.define(st='S_H', n=500)
lyo.add_entry('H', 'Human', y0_h)

y0_v = mbp_h.get_y0_proto()
y0_v.define(st='S_V', n=150)
y0_v.define(st='I_V', n=50)

lyo.add_entry('V', 'Vector', y0_v)

# Define interaction: risky bite rate changes as the number of infectious vectors change
lyo.add_interaction('H',
                    cx.WhoStartWithChecker('StInf', 'update value'),
                    cx.ABMValueImpulse('Bite', 'v1'))


print(lyo.get_parameter_hierarchy(ctrl))

model = ctrl.generate_model('M3', 'VectorBorne', bn='pVectorBorne')
y0s = ctrl.get_y0s('VectorBorne')

print(y0s)

cx.start_counting('MM')
output = cx.simulate(model, y0s, 0, 10, .5, log=False)
cx.stop_counting()
print(output)
print()
print('Event count')
print(cx.get_counting_results('MM'))


output[['H:S_H', 'H:I_H', 'H:R_H', 'V:S_V', 'V:I_V', 'H:Bite']].plot()
# output.plot()
plt.show()


model
