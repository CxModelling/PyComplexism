import numpy.random as rd
from numpy import expm1
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
        'Prv': inf / n,
        'Inf': inf
    }


mbp_sr = ebm.BlueprintODEEBM('SER')
ys = ['Sus', 'Rec']
mbp_sr.set_fn_ode(SIR_ODE, ys)
mbp_sr.set_external_variables({'Inf': 0})
mbp_sr.set_dt(dt=0.05, odt=0.05)
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
model_i = mbp_i.generate('I', pc=pc.breed('I', 'abm'), ss=dbp)


class InfIn(cx.ImpulseResponse):
    def __init__(self):
        self.Last = None

    def initialise(self, ti):
        self.Last = ti

    def __call__(self, disclosure, model_foreign, model_local, ti):
        if self.Last:
            dt = ti - self.Last
            self.Last = ti
            if dt > 0:
                sus = model_foreign.Y['Sus']
                prv = model_foreign.get_snapshot('Prv', ti)
                rate = model_foreign.Parameters['beta'] * dt * prv
                lam = rate * sus
                if lam < 5:
                    n = rd.poisson(lam)
                else:
                    n = rd.binomial(sus, -expm1(-rate))
                n = min(n, sus)
                return 'InfIn', {'n': n}
        else:
            self.Last = ti


model_sr.add_listener(cx.WhoStartWithChecker('StInf', 'update value'), cx.ValueImpulse('Inf', 'v1'))
model_sr.add_listener(cx.StartsWithChecker('remove agent'), cx.AddOneImpulse('Rec'))
model_sr.add_listener(cx.StartsWithChecker('add'), cx.MinusNImpulse('Sus', 'n'))


ii = InfIn()
#model_i.add_listener(cx.InitialChecker(), ii)
model_i.add_listener(cx.IsChecker('update'), ii)


model = cx.MultiModel('SR_I', pars=pc)
model.append_child(model_i)
model.append_child(model_sr)


y0s = cx.BranchY0()

y0 = cx.LeafY0()
y0.define({'n': 50, 'attributes': {'st': 'Inf'}})
y0s.append_child('I', y0)

y0 = cx.ODEY0()
y0.define('Sus', n=950)
y0s.append_child('SR', y0)


cx.start_counting('MM')
output = cx.simulate(model, y0s, 0, 10, 0.5)
cx.stop_counting()
# print(output)
print(output[['SR:Sus', 'I:Inf', 'SR:Rec', 'I:StInf', 'SR:Inf', 'SR:Prv']])
print()
print(cx.get_counting_results('MM'))

output[['SR:Sus', 'I:Inf', 'SR:Rec', 'I:StInf', 'SR:Inf', 'SR:Prv']].plot()
# output.plot()
plt.show()
