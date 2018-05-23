import complexism as cx
import complexism.equationbased as ebm

__author__ = 'TimeWz667'


model_name = 'EBM_SIR'

bn = cx.read_bn_script(cx.load_txt('../scripts/pSIR.txt'))
pc = ebm.prepare_pc(model_name, bn=bn)


def SIR_ODE(y, t, p, x):
    s = y[0]
    i = y[1]
    n = sum(y)
    inf = s*i*p['beta']/n * x['dis']
    rec = i*p['gamma']
    return [-inf, inf-rec, rec]


model = ebm.generate_ode_model(model_name, SIR_ODE, pc, ['S', 'I', 'R'], x={'dis': 1})


ebm.set_observations(model, stocks=['S', 'I', 'R'])

y0 = {
    'S': 990,
    'I': 10,
    'R': 0
}

print(cx.simulate(model, y0, 0, 30, 1))
