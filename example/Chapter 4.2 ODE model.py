import complexism as cx
import epidag as dag


psc = """
PCore pSIR {
    beta = 1.5
    gamma = 0.2
}
"""

bn = cx.read_pc(psc)
sm = dag.as_simulation_core(bn, hie={'city': []})
pc = sm.generate('Taipei')


def SIR_ODE(y, t, p, x):
    s = y[0]
    i = y[1]
    n = sum(y)
    inf = s*i*p['beta']/n
    rec = i*p['gamma']
    return [-inf, inf-rec, rec]


eqs = cx.OrdinaryDifferentialEquations(SIR_ODE, ['S', 'I', 'R'], dt=.1)


model_name = 'M1'

model = cx.GenericEquationBasedModel(model_name, pc, eqs, dt=.5)

model.add_observing_stock('S')
model.add_observing_stock('I')
model.add_observing_stock('R')

y0 = {
    'S': 999,
    'I': 1,
    'R': 0
}

print(cx.simulate(model, y0, 0, 10, 1))
