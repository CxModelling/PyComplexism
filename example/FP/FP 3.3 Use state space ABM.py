import complexism as cx
import complexism.agentbased.statespace as ss

__author__ = 'TimeWz667'


bn = cx.read_bn_script(cx.load_txt('../scripts/pSIR.txt'))
dbp = cx.read_dbp_script(cx.load_txt('../scripts/SIR_BN.txt'))

model_name = 'ABM_SIR'
pc = ss.prepare_pc(model_name, ag_group='agent', dbp=dbp, bn=bn)

model = ss.generate_plain_model(model_name, dbp=dbp, pc=pc, prefix='Ag', group='agent')
ss.install_behaviour(model, be_name='FOI', be_type='FDShockFast',
                     s_src='Inf', t_tar='Infect', dt=0.5)

ss.set_observations(model,
                    states=['Sus', 'Inf', 'Rec', 'Alive', 'Dead'],
                    transitions=['Infect', 'Recov', 'Die'],
                    behaviours=['FOI'])


y0 = [
    {'n': 990, 'attributes': {'st': 'Sus'}},
    {'n': 10, 'attributes': {'st': 'Inf'}},
]

print(cx.simulate(model, y0, 0, 10, 1))
