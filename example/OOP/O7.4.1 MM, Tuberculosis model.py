import numpy as np
import re
import matplotlib.pyplot as plt
import complexism as cx
import epidag as dag
import complexism.agentbased.statespace as ss
import complexism.equationbased as ebm
from complexism.mcore import EventListener
__author__ = 'TimeWz667'


bn = cx.read_bn_script(cx.load_txt('../scripts/tb/ptb.txt'))
sm = dag.as_simulation_core(bn, hie={'city': ['SER', 'I'], 'SER': [],
                                     'I': ['AgI'],
                                     'AgI': ['Cure', 'Recover',
                                             'SeekCare', 'Treat', 'Die_TB', 'Die']})


# Step 2 define equations
def TB_ODE(y, t, p, x):
    sus = y[0]
    flat = y[1]
    slat = y[2]
    rec = y[4]

    n = sus + flat + slat + rec + x['N_abm']

    infection = sus * x['Inf'] * p['r_tr']/n
    latent = flat * p['r_slat']
    activation = flat * p['r_act']
    reactivation = slat * p['r_ract']
    relapse = rec * p['r_rel']
    dr = p['r_death']
    dy = np.array([-infection + (flat + slat + rec) * dr,
                   infection - latent - activation - flat * dr,
                   latent - reactivation - slat * dr,
                   activation + reactivation + relapse,
                   - relapse - rec * dr])
    # dy[0] += (sus + flat, + slat + rec) * dr
    return dy


def TB_Measure(y, t, p, x):
    return {
        'N_ebm': sum(y),
        'N': sum(y) + x['N_abm']
    }


mbp_ser = ebm.BlueprintODEEBM('SER')
ys = ['Sus', 'LatFast', 'LatSlow', 'Inf_psu', 'Rec']
mbp_ser.set_fn_ode(TB_ODE, ['Sus', 'LatFast', 'LatSlow', 'Inf_psu', 'Rec'])
mbp_ser.set_external_variables({'Inf': 0, 'N_abm': 0})
mbp_ser.set_dt(dt=0.01, odt=0.5)
mbp_ser.add_observing_function(TB_Measure)
mbp_ser.set_observations()


# ABM

dbp_i = cx.read_dbp_script(cx.load_txt('../scripts/tb/dtb_cases.txt'))

mbp_i = ss.BlueprintStSpABM('I')
mbp_i.set_agent(prefix='Ag', group='AgI', dynamics='I')
mbp_i.add_behaviour('Dead', 'Cohort', s_death='Dead')
mbp_i.add_behaviour('Recovery', 'Cohort', s_death='PostCare')
mbp_i.set_observations(states=['Inf', 'Alive', 'PreCare', 'InCare', 'PostCare'],
                       transitions=['Cure', 'Recover', 'SeekCare', 'Die_TB'])


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


class LisI(EventListener):

    def needs(self, disclosure, model_local):
        if disclosure.is_sibling():
            return True

    def apply_shock(self, disclosure, model_foreign, model_local, ti, arg=None):
        if disclosure.What.startswith('update'):
            n = model_foreign.Y['Inf_psu']
            if n >= 1:
                model_local.birth(n, st='Act', ti=ti)


# Instantiation
pc = sm.generate('Taipei')

model_ser = mbp_ser.generate('SER', pc=pc.breed('SER', 'SER'))
model_i = mbp_i.generate('I', pc=pc.breed('I', 'I'), dc=dbp_i)

model_ser.add_listener(LisSER())
model_i.add_listener(LisI())

scale = 3000
# Step 5 simulate
y0e = {
    'Sus': 29*scale,
    'LatFast': 0,
    'LatSlow': 10*scale,
    'Inf_psu': scale,
    'Rec': 10*scale
}


y0a = [
    {'n': 0, 'attributes': {'st': 'Act'}}
]

model = cx.MultiModel('TB_v1', env=pc)
model.append(model_ser)
model.append(model_i)

model.add_observing_model('I')
model.add_observing_model('SER')

from complexism.misc.counter import *
start_counting('TB')
output = cx.simulate(model, {'SER': y0e, 'I': y0a}, 0, 20, 1)
stop_counting()
print(get_results('TB'))

output.plot()

plt.show()
