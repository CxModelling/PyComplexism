import complexism as cx
import complexism.equationbased as ebm
import matplotlib.pyplot as plt


bn = cx.read_pc(cx.load_txt('scripts/pSIR.txt'))


def SIR_ODE(y, t, p, x):
    s = y[0]
    i = y[1]
    n = sum(y)
    inf = s*i*p['beta']/n * x['dis']
    rec = i*p['gamma']
    return [-inf, inf-rec, rec]


bp = ebm.BlueprintODE('EBM ODE')
bp.set_ode(SIR_ODE)
bp.set_y_names(['S', 'I', 'R'])
bp.set_x({'dis': 0.5})


bp.set_observations(stocks=['S', 'I', 'R'])


model = bp.generate('SIR', bn=bn, dt=0.5, fdt=0.1)

y0 = {
    'S': 999,
    'I': 1,
    'R': 0
}

out = cx.simulate(model, y0, 0, 30, 1)
out.plot()
plt.show()
