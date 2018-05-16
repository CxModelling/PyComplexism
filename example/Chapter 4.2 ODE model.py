import complexism as cx
import epidag as dag
import matplotlib.pyplot as plt


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
    inf = s*i*p['beta']/n * x['dis']
    rec = i*p['gamma']
    return [-inf, inf-rec, rec]


eqs = cx.OrdinaryDifferentialEquations(SIR_ODE, ['S', 'I', 'R'], dt=.1, x={'dis': 0.5})


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

out = cx.simulate(model, y0, 0, 10, 1)
out.plot()
plt.show()

model.Equations.impulse('dis', 0.1)
out = cx.update(model, to=20, dt=1)
out.plot()
plt.show()


pc.impulse({'beta': 10.0})
out = cx.update(model, to=30, dt=1)
out.plot()
plt.show()
