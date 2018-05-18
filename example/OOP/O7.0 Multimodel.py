import epidag as dag
import complexism as cx
import complexism.equationbased as ebm
import complexism.agentbased.statespace as ss
__author__ = 'TimeWz667'


psc = '''
PCore MultiSIR {
    beta = 1.5
    betaF = 1.0/300
    gamma = 0.2
    Infect ~ exp(beta)
    InfectF ~ exp(betaF)
    Recov ~ exp(0.5)
}
'''


bn = dag.bn_from_script(psc)

hie = {
    'city': ['abm', 'ebm'],
    'abm': ['agent'],
    'agent': ['Infect', 'InfectF', 'Recov'],
    'ebm': []
}


sm = dag.as_simulation_core(bn, hie=hie)


model_name = 'MultiSIR'

pc = sm.generate(model_name)


model = cx.MultiModel(model_name, pc)


# EBM
ebm_name = 'SIR_E'


def SIR_ODE(y, t, p, x):
    s = y[0]
    i = y[1]
    n = sum(y)
    inf_d = s*p['beta']*i/n
    inf_f = s*p['betaF']*x['fI']/x['fN'] if x['fN'] else 0
    inf = inf_d + inf_f
    rec = i*p['gamma']
    return [-inf, inf-rec, rec]


def fore_imp(m, tab, ti):
    tab['fI'] = m.Equations.X['fI']
    tab['fN'] = m.Equations.X['fN']


p_ebm = pc.breed(ebm_name, 'ebm')
m_ebm = ebm.generate_ode_model(ebm_name, SIR_ODE, pc, ['S', 'I', 'R'], {'fI': 1, 'fN': 300}, dt=0.2)
ebm.set_observations(m_ebm, stocks=['S', 'I', 'R'], stock_functions=[fore_imp])


# ABM
abm_name = 'SIR_A'

dsc = '''
CTMC SIR {
    Sus
    Inf
    Rec
    
    Sus -- Infect -> Inf
    Sus -- InfectF -> Inf
    Inf -- Recov -> Rec
}
'''


def num(m, tab, ti):
    n = len(m)
    tab['N'] = n if n else 0


dbp = cx.read_dc(dsc)
p_abm = pc.breed(abm_name, 'abm')

mbp = ss.BlueprintStSpABM(abm_name)
mbp.set_agent(prefix='Ag', group='agent', dynamics='SIR')
mbp.add_behaviour('FOI', 'FDShockFast', s_src='Inf', t_tar='Infect', dt=0.5)
mbp.set_observations(states=['Sus', 'Inf', 'Rec'],
                     transitions=['Infect', 'InfectF'],
                     behaviours=['FOI'], functions=[num])


m_abm = mbp.generate(abm_name, pc=p_abm, dc=dbp)

model.append(m_ebm)
model.add_observing_model(ebm_name)
model.append(m_abm)
model.add_observing_model(abm_name)


model.link('{}@Inf'.format(abm_name), '{}@fI'.format(ebm_name))
model.link('{}@N'.format(abm_name), '{}@fN'.format(ebm_name))
model.link('{}@I'.format(ebm_name), '{}@InfectF'.format(abm_name))


y0 = {
    abm_name: [
        {'n': 300, 'attributes': {'st': 'Sus'}},
        #{'n': 10, 'attributes': {'st': 'Inf'}}
    ],
    ebm_name: {'S': 290, 'I': 10, 'R': 0}
}

m_abm.add_observing_behaviour('I-InfectF')

output = cx.simulate(model, y0, 0, 10, 1)
print(output)
