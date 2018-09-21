import numpy.random as rd
from numpy import expm1
import complexism as cx
import matplotlib.pyplot as plt

__author__ = 'TimeWz667'


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


ctrl = cx.Director()
ctrl.load_bayes_net('scripts/pCloseSIR.txt')
ctrl.load_state_space_model('scripts/CloseSIR.txt')
print(ctrl.list_bayes_nets())
print(ctrl.list_state_spaces())


mbp_sr = ctrl.new_sim_model('SR', 'ODEEBM')
ys = ['Sus', 'Rec']
mbp_sr.set_fn_ode(SIR_ODE, ys)
mbp_sr.set_external_variables({'Inf': 0})
mbp_sr.set_dt(dt=0.05, odt=0.05)
mbp_sr.add_observing_function(SIR_Meas)
mbp_sr.set_observations(stocks=ys)


# ABM
mbp_i = ctrl.new_sim_model('I', 'StSpABM')
mbp_i.set_agent(prefix='Ag', group='agent', dynamics='CloseSIR')
mbp_i.add_behaviour('Recovery', 'Cohort', s_death='Rec')
mbp_i.add_behaviour('StInf', 'StateTrack', s_src='Inf')
mbp_i.add_behaviour('InfIn', 'AgentImport', s_birth='Inf')
mbp_i.set_observations(states=['Inf', 'Rec'],
                       transitions=['Recov'],
                       behaviours=['InfIn', 'StInf'])


lyo = ctrl.new_model_layout('HybridSIR')

y0_sr = mbp_sr.get_y0_proto()
y0_sr.define('Sus', n=900)
lyo.add_entry('E', 'SR', y0_sr)

y0_i = mbp_i.get_y0_proto()
y0_i.define(st='Inf', n=100)
lyo.add_entry('A', 'I', y0_i)

lyo.add_interaction('E',
                    cx.WhoStartWithChecker('StInf', 'update value'),
                    cx.ValueImpulse('Inf', 'v1'))

lyo.add_interaction('E',
                    cx.StartsWithChecker('remove agent'),
                    cx.AddOneImpulse('Rec'))


lyo.add_interaction('E',
                    cx.StartsWithChecker('add'),
                    cx.MinusNImpulse('Sus', 'n'))

lyo.add_interaction('A', cx.IsChecker('update'), InfIn())

for m, _, _ in lyo.models():
    print(m)

print(lyo.get_parameter_hierarchy(ctrl))

model = ctrl.generate_model('M2', 'HybridSIR', bn='pCloseSIR')
y0s = ctrl.get_y0s('HybridSIR')

print(y0s)

cx.start_counting('MM')
output = cx.simulate(model, y0s, 0, 10, .5, log=False)
cx.stop_counting()
print(output)
print()
print(cx.get_counting_results('MM'))

# print(output)

output[['E:Sus', 'E:Rec', 'A:Inf', 'E:Inf']].plot()
# output.plot()
plt.show()
