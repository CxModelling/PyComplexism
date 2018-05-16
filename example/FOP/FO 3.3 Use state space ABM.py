import complexism as cx
import complexism.agentbased.statespace as ss

__author__ = 'TimeWz667'


bn = cx.read_pc(cx.load_txt('../scripts/pSIR.txt'))
dc = cx.read_dc(cx.load_txt('../scripts/SIR_BN.txt'))

mbp = ss.BlueprintStSpABM('ABM_SIR')
mbp.set_agent('Ag ', 'agent', dynamics='SIR')
mbp.add_behaviour('FOI', 'FDShockFast', s_src='Inf', t_tar='Infect', dt=0.5)
mbp.set_observations(states=['Sus', 'Inf', 'Rec', 'Alive', 'Dead'],
                     transitions=['Infect', 'Recov', 'Die'],
                     behaviours=['FOI'])


model = mbp.generate('M1', bn=bn, dc=dc)


y0 = [
    {'n': 990, 'attributes': {'st': 'Sus'}},
    {'n': 10, 'attributes': {'st': 'Inf'}},
]

print(cx.simulate(model, y0, 0, 10, 1))
