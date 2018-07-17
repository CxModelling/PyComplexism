import numpy.random as rd
import matplotlib.pyplot as plt
import epidag as dag
import complexism as cx
import complexism.equationbased as ebm
import complexism.agentbased.statespace as ss


__author__ = 'TimeWz667'

psc = '''
PCore SIR {
    beta = 1.5
    gamma = 0.5
    Infect ~ exp(beta)
    Recov ~ exp(gamma)
}
'''

bn = dag.bn_from_script(psc)

hie = {
    'city': ['ebm', 'abm'],
    'abm': ['agent'],
    'agent': ['Infect', 'Recov'],
    'ebm': []
}

sm = dag.as_simulation_core(bn, hie=hie)


def SIR_ODE(y, t, p, x):
    return [0, 0]


def SIR_Meas(y, t, p, x):
    inf = x['Inf']
    n = sum(y) + inf
    return {
        'n': n,
        'incR': inf / n,
        'inc': inf
    }


mbp_sr = ebm.BlueprintODEEBM('SER')
ys = ['Sus', 'Rec']
mbp_sr.set_fn_ode(SIR_ODE, ys)
mbp_sr.set_external_variables({'Inf': 0})
mbp_sr.set_dt(dt=0.01, odt=0.25)
mbp_sr.add_observing_function(SIR_Meas)
mbp_sr.set_observations()


# ABM
abm_name = 'SIR_A'

dsc = '''
CTMC SIR {
    Inf
    Rec

    Inf -- Recov -> Rec
}
'''


mbp_i = ss.BlueprintStSpABM('I')
mbp_i.set_agent(prefix='Ag', group='agent', dynamics='SIR')
mbp_i.add_behaviour('Recovery', 'Cohort', s_death='Rec')
mbp_i.add_behaviour('StInf', 'StateTrack', s_src='Inf')
mbp_i.add_behaviour('InfIn', 'AgentImport', s_birth='Inf')
mbp_i.set_observations(states=['Inf', 'Rec'],
                       transitions=['Recov'],
                       behaviours=['InfIn', 'StInf'])


dbp = cx.read_dbp_script(dsc)


pc = sm.generate('SIR')
model_sr = mbp_sr.generate('SR', pc=pc.breed('SR', 'ebm'))
model_i = mbp_i.generate('I', pc=pc.breed('I', 'abm'), dc=dbp)


class InfOut(cx.ImpulseResponse):
    def __call__(self, disclosure, model_foreign, model_local, ti):
        n = disclosure.Arguments['n']
        model_local.impulse('del', y='Sus', n=float(n))
        model_local.impulse('impulse', k='Inf', v=model_foreign.get_snapshot('StInf', ti))


class InfIn(cx.ImpulseResponse):
    def __init__(self):
        self.Last = None

    def __call__(self, disclosure, model_foreign, model_local, ti):
        if self.Last:
            dt = ti - self.Last
            if dt:
                sus = model_foreign.Y['Sus']
                inf = model_local.get_snapshot('Inf', ti)
                rec = model_foreign.Y['Rec']
                lam = model_foreign['beta'] * sus * inf * dt / (sus + inf + rec)
                n = rd.poisson(lam)
                n = min(n, sus)
                model_local.shock(ti, model_foreign, 'InfIn', value=n)

        self.Last = ti


class RecSource(cx.ImpulseResponse):
    def __call__(self, disclosure, model_foreign, model_local, ti):
        model_local.impulse('add', y='Rec', n=1)
        model_local.impulse('impulse', k='Inf', v=model_foreign.get_snapshot('StInf', ti))


class UpdateSource(cx.ImpulseResponse):
    def __call__(self, disclosure, model_foreign, model_local, ti):
        model_local.impulse('impulse', k='Inf', v=model_foreign.get_snapshot('StInf', ti))


model_sr.add_listener(cx.InitialChecker(), UpdateSource())
model_sr.add_listener(cx.StartsWithChecker('add'), InfOut())
model_sr.add_listener(cx.StartsWithChecker('Rec'), RecSource())


ii = InfIn()
model_i.add_listener(cx.InitialChecker(), ii)
model_i.add_listener(cx.StartsWithChecker('update'), ii)


model = cx.MultiLevelModel('SR_I', env=pc)
model.append(model_i)
model.append(model_sr)


y0 = {
    'I': [
        {'n': 10, 'attributes': {'st': 'Inf'}}
    ],
    'SR': {'Sus': 990, 'Rec': 0}
}


cx.start_counting('MM')
output = cx.simulate(model, y0, 0, 10, 1)
cx.stop_counting()
print(output[['SR.Sus', 'I.Inf', 'SR.Rec', 'I.StInf', 'SR.inc']])
print()
print(cx.get_results('MM'))

output[['SR.Sus', 'I.Inf', 'SR.Rec', 'I.StInf', 'SR.inc']].plot()
plt.show()
