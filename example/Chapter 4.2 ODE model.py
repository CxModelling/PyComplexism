import epidag as dag
import complexism as cx
import complexism.equationbased as ebm
import matplotlib.pyplot as plt


pc = dag.quick_build_parameter_core(cx.load_txt('scripts/pSIR.txt'))


def SIR_ODE(y, t, p, x):
    s = y[0]
    i = y[1]
    n = sum(y)
    inf = s*i*p['beta']/n * x['dis']
    rec = i*p['gamma']
    return [-inf, inf-rec, rec]


bp = ebm.BlueprintODEEBM('EBM ODE')
bp.set_fn_ode(SIR_ODE, ['S', 'I', 'R'])
bp.set_external_variables({'dis': 0.5})
bp.set_dt(dt=0.1, odt=0.5)
bp.set_observations()


model = bp.generate('SIR', pc=pc)

y0 = {
    'S': 999,
    'I': 1,
    'R': 0
}

cx.simulate(model, y0, 0, 15, 1, log=True)
model.impulse('del', y='S', n=500)
model.impulse('add', y='I', n=100)
out = cx.update(model, 30, 1)
out.plot()
plt.show()
