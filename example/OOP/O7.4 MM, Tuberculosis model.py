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
    r_tr = 10
    r_slat = 0.2
    
    r_act = 0.073
    r_ract = 0.0073
    r_rel = 0.0073
    r_death = 0.025

    r_cure = 0.2

    patient_delay = 5/12
    SeekCare ~ exp(1/patient_delay)
    
    treatment_period = 0.5
    Treat ~ k(treatment_period)
    
    Cure ~ exp(r_cure)
    Recover ~ k(1/24)
    
    Die_TB ~ exp(0.5)
    Die ~ exp(r_death)
}
"""

bn = cx.read_bn_script(psc)
sm = dag.as_simulation_core(bn, hie={'city': ['SER', 'I'], 'SER': [],
                                     'I': ['AgI'],
                                     'AgI': ['Cure', 'Recover',
                                             'SeekCare', 'Treat', 'Die_TB', 'Die']})
pc = sm.generate('Taipei')


# Step 2 define equations
def TB_ODE(y, t, p, x):
    sus = y[0]
    flat = y[1]
    slat = y[2]
    rec = y[4]

    n = sum(y) + x['N_abm']

    infection = sus * x['Inf'] * p['r_tr']/n
    latent = flat * p['r_slat']
    activation = flat * p['r_act']
    reactivation = slat * p['r_ract']
    relapse = rec * p['r_rel']
    dr = p['r_death']
    dy = np.array([-infection - sus * dr,
                   infection - latent - activation - flat * dr,
                   latent - reactivation - slat * dr,
                   activation + reactivation + relapse,
                   - relapse - rec * dr])
    dy[0] += 5000 - n
    return dy


def cal_N(m, tab, ti):
    tab['N'] = sum(m.Y[k] for k in ['Sus', 'LatFast', 'LatSlow', 'Rec'])


ys = ['Sus', 'LatFast', 'LatSlow', 'Inf_psu', 'Rec']

eqs = cx.OrdinaryDifferentialEquations(TB_ODE, ys, dt=.1, x={'Inf': 0,'N_abm': 0})

model_ser = cx.GenericEquationBasedModel('SER', dt=0.5, eqs=eqs, env=pc.breed('SER', 'SER'))

for st in ys:
    model_ser.add_observing_stock(st)
model_ser.add_observing_stock_function(cal_N)


# ABM

d_i = '''
CTBN Active {
    life[Alive | Dead]
    tb[Act | Deact]
    care[Out | In | Completed]

    Alive{life:Alive}
    Dead{life:Dead}
    
    Act{life:Alive, tb:Act, care:Out}

        
    PreCare{care: Out}
    InCare{care: In}
    PostCare{care: Completed}
    
    Inf{tb:Act}
    Safe{tb:Deact}
    Treating{tb:Act, care:In}
      
    Inf -- Cure -> Safe
    Treating -- Recover -> Safe 
    PreCare -- SeekCare -> InCare
    InCare -- Treat -> PostCare
    
    Alive -- Die -> Dead # from transition Die to state Dead by distribution Die
    Inf -- Die_TB -> Dead   
'''


dbp_i = cx.read_dbp_script(d_i)

mbp_i = ss.BlueprintStSpABM('I')
mbp_i.set_agent(prefix='Ag', group='AgI', dynamics='I')
mbp_i.add_behaviour('Dead', 'Cohort', s_death='Dead')
mbp_i.add_behaviour('Recovery', 'Cohort', s_death='PostCare')
mbp_i.set_observations(states=['Inf', 'Alive', 'PreCare', 'InCare', 'PostCare'],
                       transitions=['Cure', 'Recover', 'SeekCare', 'Die_TB'])

model_i = mbp_i.generate('I', pc=pc.breed('I', 'I'), dc=dbp_i)


class LisSER(EventListener):

    def needs(self, disclosure, model_local):
        if disclosure.is_sibling():
            return True

    def apply_shock(self, disclosure, model_foreign, model_local, ti, arg=None):
        if disclosure.What.startswith('initialise'):
            pass
        elif disclosure.What.startswith('Die'):
            model_local.go_to(ti)
            model_local.impulse('add', y='Sus', n=1)  # Reincarnation

        elif disclosure.What.startswith('Treat'):
            model_local.go_to(ti)
            model_local.impulse('add', y='Rec', n=1)

        elif disclosure.What.startswith('Add'):
            model_local.go_to(ti)
            n = re.match('Add (\d+) agents', disclosure.What).group(1)
            model_local.impulse('del', y='Inf_psu', n=float(n))

        elif disclosure.What in ['Recover', 'Cure']:
            model_local.go_to(ti)
        else:
            return
        model_local.impulse('impulse', k='Inf', v=model_foreign.get_snapshot('Inf', ti))
        model_local.impulse('impulse', k='N_abm', v=model_foreign.get_snapshot('Alive', ti))


model_ser.add_listener(LisSER())


class LisI(EventListener):

    def needs(self, disclosure, model_local):
        if disclosure.is_sibling():
            return True

    def apply_shock(self, disclosure, model_foreign, model_local, ti, arg=None):
        if disclosure.What.startswith('update'):
            n = model_foreign.Y['Inf_psu']
            if n >= 1:
                model_local.birth(n, st='Act', ti=ti)


model_i.add_listener(LisI())

# Step 5 simulate
y0e = {
    'Sus': 2900,
    'LatFast': 0,
    'LatSlow': 1000,
    'Inf_psu': 100,
    'Rec': 1000
}


y0a = [
    {'n': 0, 'attributes': {'st': 'Act'}}
]

model = cx.MultiModel('TB', env=pc)
model.append(model_ser)
model.append(model_i)

model.add_observing_model('I')
model.add_observing_model('SER')

output = cx.simulate(model, {'SER': y0e, 'I': y0a}, 0, 100, 1)

output.plot()

plt.show()
