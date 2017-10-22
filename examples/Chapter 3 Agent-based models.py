from dzdy import *
from dzdy.abmodel import install_behaviour
import dzdy.abmodel as ab

__author__ = 'TimeWz667'

ctrl = DirectorDCPC()
ctrl.load_pc('scripts/pSIR.txt')
ctrl.load_dc('scripts/SIR_BN.txt')


pc = ctrl.get_pc('pSIR').sample_core()
dc = ctrl.get_dc('SIR_BN').generate_model(pc)


abm = AgentBasedModel('SIR', dc, pc)
print(abm)
install_network(abm, 'N1', 'Category', p=0.2)
install_behaviour(abm, 'Net', 'NetShock', s_src='Inf', t_tar='Infect', net='N1')
abm.add_obs_behaviour('Net')
abm.add_obs_state('Inf')
abm.add_obs_state('Sus')
abm.add_obs_transition('Infect')
simulate(abm, {'Sus': 50, 'Inf': 50}, fr=0, to=10)
print(abm.output())


ctrl = DirectorDCPC()
ctrl.load_pc('scripts/pBAD.txt')
ctrl.load_dc('scripts/BAD.txt')


pc = ctrl.get_pc('pBAD').sample_core()
dc = ctrl.get_dc('BAD').generate_model(pc)

abm = AgentBasedModel('BAD', dc, pc)
print(abm)


demo = DemographySimplified('../data/Life_All.csv')


install_behaviour(abm, 'BD', 'DemoDynamic', s_birth='Young', s_death='Dead', t_death='Die', demo=demo)
abm.add_obs_behaviour('BD')
abm.add_obs_state('Alive')
abm.add_obs_state('Death')
abm.add_obs_transition('Die')
simulate(abm, {'Young': 1000}, fr=0, to=10)
print(abm.output())
