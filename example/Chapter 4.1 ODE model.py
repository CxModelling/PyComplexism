import complexism as cx
import matplotlib.pyplot as plt


def SIR_ODE(y, t, p, x):
    s = y[0]
    i = y[1]
    n = sum(y)
    inf = s*i*p['beta']/n * x['dis']
    rec = i*p['gamma']
    return [-inf, inf-rec, rec]


ctrl = cx.Director()
ctrl.load_bayes_net('scripts/pSIR.txt')

bp = ctrl.new_sim_model('EBM SIR', 'ODEEBM')
bp.set_fn_ode(SIR_ODE, ['S', 'I', 'R'])
bp.set_external_variables({'dis': 0.5})
bp.set_dt(dt=0.1, odt=0.5)
bp.set_observations()


if __name__ == '__main__':
    model = ctrl.generate_model('M1', 'EBM SIR', bn='pSIR')

    y0 = cx.ODEY0()
    y0.define(st='S', n=999)
    y0.define(st='I', n=1)

    cx.simulate(model, y0, 0, 10, .1, log=True)
    model.shock(10, 'del', y='S', n=100)
    model.shock(10, 'add', y='I', n=100)
    out = cx.update(model, 30, 1)
    out.plot()
    plt.show()
