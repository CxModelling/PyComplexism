import numpy as np
import re
import matplotlib.pyplot as plt
import complexism as cx
import epidag as dag
import complexism.agentbased.statespace as ss
from complexism.mcore import EventListener
__author__ = 'TimeWz667'


model_name = 'TB'

# Step 1 set a parameter core
psc = """
PCore pTB {
    r_tr = 2
    r_slat = 0.2
    
    r_act = 0.073
    r_ract = 0.0073
    r_rel = 0.0073
    
    r_rec = 0.2
    Cure ~ exp(0.2)
    Recover ~ exp(0.5)
    r_death = 0.025
    r_tb_death = 0.2
}
"""

bn = cx.read_bn_script(psc)
sm = dag.as_simulation_core(bn, hie={'city': ['SER', 'I'], 'SER': [], 'I': ['AgI'], 'AgI': ['Cure', 'Recover']})
pc = sm.generate('Taipei')


# Step 2 define equations
def TB_ODE(y, t, p, x):
    sus = y[0]
    flat = y[1]
    slat = y[2]
    inf = y[3]
    rec = y[4]

    n = sum(y)

    infection = sus * x['Inf'] * p['r_tr']/n
    latent = flat * p['r_slat']
    activation = flat * p['r_act']
    reactivation = slat * p['r_ract']
    relapse = rec * p['r_rel']
    recovery = inf * p['r_rec']
    death_tb = inf * p['r_tb_death']
    dy = np.array([-infection,
                   infection - latent - activation,
                   latent - reactivation,
                   activation + reactivation + relapse - death_tb,
                   - relapse])
    dy[0] += death_tb + n*p['r_death']
    dy -= y * p['r_death']
    return dy


def cal_N(m, tab, ti):
    tab['N'] = sum(m.Y.values())


ys = ['Sus', 'LatFast', 'LatSlow', 'Inf_psu', 'Rec']

eqs = cx.OrdinaryDifferentialEquations(TB_ODE, ys, dt=.1, x={'Inf': 0})

model_ser = cx.GenericEquationBasedModel('SER', dt=0.5, eqs=eqs, env=pc.breed('SER', 'SER'))

for st in ys:
    model_ser.add_observing_stock(st)
model_ser.add_observing_stock_function(cal_N)


# ABM

d_i = '''
CTMC I {
    Inf
    Export
    Inf -- Recover -> Export
    Inf -- Cure -> Export
}
'''

dbp_i = cx.read_dbp_script(d_i)

mbp_i = ss.BlueprintStSpABM('I')
mbp_i.set_agent(prefix='Ag', group='AgI', dynamics='I')
mbp_i.add_behaviour('Activation', 'AgentImport', s_birth='Inf')
mbp_i.add_behaviour('Recovery', 'Cohort', s_death='Export')
mbp_i.set_observations(states=['Inf'], transitions=[], behaviours=[])

model_i = mbp_i.generate('I', pc=pc.breed('I', 'I'), dc=dbp_i)


class LisSER(EventListener):

    def needs(self, disclosure, model_local):
        if disclosure.is_sibling():
            return True

    def apply_shock(self, disclosure, model_foreign, model_local, ti, arg=None):
        if disclosure.What.startswith('initialise'):
            pass
        elif disclosure.What.startswith('Remove'):
            model_local.go_to(ti)
            model_local.impulse('add', y='Rec', n=1)
        elif disclosure.What.startswith('Add'):
            model_local.go_to(ti)
            n = re.match('Add (\d+) agents', disclosure.What).group(1)
            model_local.impulse('del', y='Inf_psu', n=float(n))
        else:
            return
        model_local.impulse('impulse', k='Inf', v=model_foreign.get_snapshot('Inf', ti))


model_ser.add_listener(LisSER())


class LisI(EventListener):

    def needs(self, disclosure, model_local):
        if disclosure.is_sibling():
            return True

    def apply_shock(self, disclosure, model_foreign, model_local, ti, arg=None):
        if disclosure.What.startswith('update'):
            n = model_foreign.Y['Inf_psu']
            if n >= 1:
                model_local.birth(n, st='Inf', ti=ti)
            # print(model_foreign.Y['Inf_psu'])


model_i.add_listener(LisI())

# Step 5 simulate
y0e = {
    'Sus': 690,
    'LatFast': 0,
    'LatSlow': 150,
    'Inf_psu': 0,
    'Rec': 150
}


y0a = [
    {'n': 20, 'attributes': {'st': 'Inf'}}
]

model = cx.MultiModel('TB', env=pc)
model.append(model_ser)
model.append(model_i)

model.add_observing_model('I')
model.add_observing_model('SER')

output = cx.simulate(model, {'SER': y0e, 'I': y0a}, 0, 50, 1)

output.plot()

plt.show()
