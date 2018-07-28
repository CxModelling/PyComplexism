import epidag as dag
import complexism as cx
import complexism.agentbased.statespace as ss


__author__ = 'TimeWz667'


bn = dag.bn_from_script(cx.load_txt('../scripts/pSIR_net.txt'))

hie = {
    'abm': ['agent'],
    'agent': ['Infect', 'Recov', 'Die'],
}

sm = dag.as_simulation_core(bn, hie=hie)
dbp = cx.read_dbp_script(cx.load_txt('../scripts/SIR_BN.txt'))

# ABM
mbp = ss.BlueprintStSpABM('SIR')
mbp.set_agent(prefix='Ag', group='agent', dynamics='SIR')
mbp.add_behaviour('Recovery', 'Reincarnation', s_death='Dead', s_birth='Sus')
mbp.add_network('net', 'GNP', p='p_connect')
mbp.add_behaviour('TM', 'NetShock', s_src='Inf', t_tar='Infect', net='net')
mbp.set_observations(states=['Inf', 'Rec'], transitions=['Recov'], behaviours=['TM'])


model = mbp.generate('Measles', dc=dbp, sm=sm)

y0 = [
    {'n': 290, 'attributes': {'st': 'Sus'}},
    {'n': 10, 'attributes': {'st': 'Inf'}}
]


output = cx.simulate(model, y0, 0, 10, 1)
print(output)

