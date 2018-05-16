import complexism as cx
import complexism.agentbased.statespace as ss
import epidag as dag

__author__ = 'TimeWz667'


bn = cx.read_pc(cx.load_txt('../scripts/pSIR.txt'))

sm = dag.as_simulation_core(bn,
                            hie={'city': ['agent'],
                                 'agent': ['Recov', 'Die', 'Infect']})

dbp = cx.read_dc(cx.load_txt('../scripts/SIR_BN.txt'))
pc = dag.quick_build_parameter_core(cx.load_txt('../scripts/pSIR.txt'))
dc = dbp.generate_model('M1', **pc.get_samplers())


def step(agent):
    evt = agent.Next
    agent.execute_event()
    agent.drop_next()
    agent.update_time(evt.Time)
    return evt.Time


ag = ss.StSpAgent('Helen', dc['Sus'], pc)
ag.initialise(0)

print('Agent is a {}'.format(ag.State))
ti = 0
while ti < 100:
    ti = step(ag)
    print('Time:', ti)
    print('Agent is a {}'.format(ag.State))
