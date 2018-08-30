import complexism as cx
from complexism.misc import start_counting, stop_counting, get_results
import complexism.equationbased as ebm
import complexism.agentbased.statespace as ss

__author__ = 'TimeWz667'


ctrl = cx.Director()
ctrl.load_bayes_net('scripts/pDzAB.txt')
ctrl.load_state_space_model('scripts/DzAB.txt')
print(ctrl.list_bayes_nets())

bp = ctrl.new_sim_model('DzAB', 'StSpABM')
bp.set_agent('DzAB')
bp.set_observations(states=['ab', 'AB'])


y0 = ss.StSpY0()
y0.define(100, st='ab')

lyo = ctrl.new_model_layout('MultiDzAB')
lyo.add_entry('M', 'DzAB', y0, fr=1, to=3)

for m, _, _ in lyo.models():
    print(m)

print(lyo.get_parameter_hierarchy(ctrl))

model = ctrl.generate_model('3DzAB', 'MultiDzAB', bn='pDzAB')
y0s = ctrl.get_y0s('MultiDzAB')

print(y0s)

start_counting('MM')
output = cx.simulate(model, y0s, 0, 10, 1)
stop_counting()
print(output)
print()
print(get_results('MM'))
