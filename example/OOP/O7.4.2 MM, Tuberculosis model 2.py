import numpy as np
import numpy.random as rd
import matplotlib.pyplot as plt
import complexism as cx
import epidag as dag
import complexism.agentbased.statespace as ss
import complexism.equationbased as ebm

__author__ = 'TimeWz667'


# Step 1 set a parameter core
bn = cx.read_bn_script(cx.load_txt('../scripts/tb/ptb.txt'))
sm = dag.as_simulation_core(bn, hie={'city': ['SER', 'I'], 'SER': [],
                                     'I': ['AgI'],
                                     'AgI': ['Cure', 'Recover',
                                             'SeekCare', 'Treat', 'Die_TB', 'Die']})


# Step 2 define equations
def TB_ODE(y, t, p, x):
    sus, flat, slat, rec = y

    n = sum(y) + x['N_abm']

    infection = sus * x['Inf'] * p['r_tr'] / n
    latent = flat * p['r_slat']
    dr = p['r_death']
    dy = np.array([-infection - sus * dr,
                   infection - latent - flat * dr,
                   latent - slat * dr,
                   - rec * dr])
    dy[0] += sum(y) * dr
    return dy


def TB_Measure(y, t, p, x):
    return {
        'N_ebm': sum(y),
        'N': sum(y) + x['N_abm']
    }


mbp_ser = ebm.BlueprintODEEBM('SER')
ys = ['Sus', 'LatFast', 'LatSlow', 'Rec']
mbp_ser.set_fn_ode(TB_ODE, ys)
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


class UpdateSource(cx.ImpulseResponse):
    def __call__(self, disclosure, model_foreign, model_local, ti):
        model_local.impulse('impulse', k='Inf', v=model_foreign.get_snapshot('Inf', ti))
        model_local.impulse('impulse', k='N_abm', v=model_foreign.get_snapshot('Alive', ti))


class InfOut(cx.ImpulseResponse):
    def __call__(self, disclosure, model_foreign, model_local, ti):
        n = disclosure.Arguments['n']
        tp = disclosure.Arguments['type']
        if tp == 'New':
            model_local.impulse('del', y='LatFast', n=float(n))
        elif tp == 'Reactivate':
            model_local.impulse('del', y='LatSlow', n=float(n))
        elif tp == 'Relapse':
            model_local.impulse('del', y='Rec', n=float(n))
        else:
            raise ValueError('Unknown type')

        model_local.impulse('impulse', k='Inf', v=model_local.Equations['Inf'] + n)
        model_local.impulse('impulse', k='N_abm', v=model_local.Equations['N_abm'] + n)


class SusSource(cx.ImpulseResponse):
    def __call__(self, disclosure, model_foreign, model_local, ti):
        model_local.impulse('add', y='Sus', n=1)
        model_local.impulse('impulse', k='Inf', v=model_foreign.get_snapshot('Inf', ti))
        model_local.impulse('impulse', k='N_abm', v=model_local.Equations['N_abm'] - 1)


class RecSource(cx.ImpulseResponse):
    def __call__(self, disclosure, model_foreign, model_local, ti):
        model_local.impulse('add', y='Rec', n=1)
        model_local.impulse('impulse', k='Inf', v=model_foreign.get_snapshot('Inf', ti))
        model_local.impulse('impulse', k='N_abm', v=model_local.Equations['N_abm'] - 1)


class TempRec(cx.ImpulseResponse):
    def __call__(self, disclosure, model_foreign, model_local, ti):
        model_local.impulse('add', y='Rec', n=1)
        model_local.impulse('impulse', k='Inf', v=model_local.Equations['Inf'] - 1)


class InfIn(cx.ImpulseResponse):
    def __call__(self, disclosure, model_foreign, model_local, ti):
        y = model_foreign.Y['LatFast']
        lam = model_foreign['r_act'] * y / 2
        n = rd.poisson(lam)
        n = min(n, y)
        if n >= 1:
            model_local.birth(n, ti=ti, st='Act', type='New')

        y = model_foreign.Y['LatSlow']
        lam = model_foreign['r_ract'] * y / 2
        n = rd.poisson(lam)
        n = min(n, y)
        if n >= 1:
            model_local.birth(n, ti=ti, st='Act', type='Reactivate')

        y = model_foreign.Y['Rec']
        lam = model_foreign['r_rel'] * y / 2
        n = rd.poisson(lam)
        n = min(n, y)
        if n >= 1:
            model_local.birth(n, ti=ti, st='Act', type='Relapse')


pc = sm.generate('Taipei')

model_ser = mbp_ser.generate('SER', pc=pc.breed('SER', 'SER'))
model_i = mbp_i.generate('I', pc=pc.breed('I', 'I'), dc=dbp_i)

model_ser.add_listener(cx.InitialChecker(), UpdateSource())
model_ser.add_listener(cx.StartsWithChecker('add'), InfOut())
model_ser.add_listener(cx.StartsWithChecker('Die'), SusSource())
model_ser.add_listener(cx.StartsWithChecker('Treat'), RecSource())
model_ser.add_listener(cx.InclusionChecker(['Recover', 'Cure']), TempRec())

ii = InfIn()
model_i.add_listener(cx.InitialChecker(), ii)
model_i.add_listener(cx.StartsWithChecker('update'), ii)

scale = 2000
# Step 5 simulate
y0e = {
    'Sus': 29 * scale,
    'LatFast': 0,
    'LatSlow': 10 * scale,
    'Rec': 10 * scale
}


y0a = [
    {'n': scale, 'attributes': {'st': 'Act', 'type': 'New'}}
]

model = cx.MultiLevelModel('TB_v2', env=pc)
model.append(model_ser)
model.append(model_i)


cx.start_counting('TB')
output = cx.simulate(model, {'SER': y0e, 'I': y0a}, 0, 20, 1, log=False)
cx.stop_counting()
print(cx.get_results('TB'))


fig, axes = plt.subplots(nrows=3, ncols=1)

output[['SER.N', 'SER.Sus', 'SER.LatFast', 'SER.LatSlow', 'SER.Rec']].plot(ax=axes[0])
output[['I.PreCare', 'I.InCare', 'I.Alive']].plot(ax=axes[1])
output[['I.Cure', 'I.Recover', 'I.SeekCare', 'I.Die_TB']].plot(ax=axes[2])

plt.show()
