import epidag as dag
import complexism as cx
import complexism.equationbased as ebm
import complexism.agentbased.statespace as ss
__author__ = 'TimeWz667'


psc = '''
PCore MultiSIR {
    beta = 1.5
    betaF = 1.0
    gamma = 0.2
    Infect ~ exp(beta)
    InfectF ~ exp(betaF)
    Recov ~ exp(0.5)
}
'''


bn = dag.bn_from_script(psc)

hie = {
    'City': ['abm', 'ebm'],
    'abm': ['agent'],
    'agent': ['Infect', 'InfectF', 'Recov'],
    'ebm': []
}

sm = dag.as_simulation_core(bn, hie=hie)


model_name = 'MultiSIR'

pc = sm.generate(model_name)


model = cx.ModelSet(model_name, pc)


# EBM
ebm_name = 'SIR_E'


def SIR_ODE(y, t, p, x):
    s = y[0]
    i = y[1]
    n = sum(y)
    inf_d = s*p['beta']*i/n
    inf_f = s*p['betaF']*x['fI']/x['fN']
    inf = inf_d + inf_f
    rec = i*p['gamma']
    return [-inf, inf-rec, rec]


p_ebm = pc.breed(ebm_name, 'ebm')
m_ebm = ebm.generate_ode_model(ebm_name, SIR_ODE, pc, ['S', 'I', 'R'])
ebm.set_observations(m_ebm, stocks=['S', 'I', 'R'])

model.append(m_ebm)


# ABM
abm_name = 'SIR_A'

dsc = '''
CTMC SIR {
    Sus -- Infect(beta) -> Inf
    Sus -- Infect(betaF) -> Inf
    Inf -- Recov(gamma) -> Rec
}
'''

dbp = cx.read_dc(dsc)
p_abm = pc.breed(abm_name, 'abm')

mbp = ss.BlueprintStSpABM(abm_name)
mbp.set_agent(prefix='Ag', group='agent', dynamics='SIR')
mbp.add_behaviour('FOI', 'FDShockFast', s_src='Inf', t_tar='Infect', dt=0.5)
mbp.set_observations(states=['Sus', 'Inf', 'Rec'],
                     transitions=['Infect', 'Recov'],
                     behaviours=['FOI'])


m_abm = mbp.generate('M1', pc=p_abm, dc=dbp)

model.append(m_ebm)


output = cx.simulate(model, 0, 10, 1)
print(output)
