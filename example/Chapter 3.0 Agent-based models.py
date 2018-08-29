import complexism as cx
import complexism.agentbased.statespace as ss

__author__ = 'TimeWz667'

ctrl = cx.Director()
ctrl.load_bates_net('scripts/pSIR_net.txt')
ctrl.load_state_space_model('scripts/SIR_BN.txt')


abm = ctrl.new_sim_model('SIR', 'StSpABM')
abm.set_agent(dynamics='SIR')
abm.add_network('N1', 'GNP', p=0.1)
abm.add_behaviour('Net', 'NetShock', s_src='Inf', t_tar='Infect', net='N1')
abm.set_observations(states=['Sus', 'Inf'], transitions=['Infect'], behaviours=['Net'])

model = ctrl.generate_model('sir', sim_model='SIR', bn='pSIR_net')

y0 = ss.StSpY0()
y0.define(n=90, st='Sus')
y0.define(n=10, st='Inf')

cx.simulate(model, y0, fr=0, to=10)
print(model.output())
