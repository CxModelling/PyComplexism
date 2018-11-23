import complexism as cx
import pandas as pd
import matplotlib.pyplot as plt

__author__ = 'TimeWz667'

mat_a = pd.read_csv('../data/LCA/lCA.Age.csv')
mat_t = pd.read_csv('../data/LCA/LCA.Time.csv')

mat_bf = pd.read_csv('../data/LCA/BirR.Female.csv')
mat_bm = pd.read_csv('../data/LCA/BirR.Male.csv')

mat_af = pd.read_csv('../data/LCA/PopStart.Female.csv')
mat_am = pd.read_csv('../data/LCA/PopStart.Male.csv')
mat_af = mat_af.fillna(0)
mat_am = mat_am.fillna(0)

dlc = cx.DemographyLeeCarter()

dlc.load_death_female(mat_a, mat_t, i_year='Year', i_age='Age', i_al='ax_f', i_be='bx_f', i_ka='female')
dlc.load_death_male(mat_a, mat_t, i_year='Year', i_age='Age', i_al='ax_m', i_be='bx_m', i_ka='male')

dlc.load_birth_female(mat_bf, i_year='Year', i_rate='br')
dlc.load_birth_male(mat_bm, i_year='Year', i_rate='br')

dlc.load_pop_female(mat_af, i_year='Year', ages=range(0, 100))
dlc.load_pop_male(mat_am, i_year='Year', ages=range(0, 100))

dlc.complete_loading()


def SIR_ODE(y, t, p, x):
    lc = x['life']
    f = y[0]
    m = y[1]

    ns = lc.get_population(t)
    n_f, n_m = ns['Female'], ns['Male']

    dr_f, dr_m = lc.get_death_rate(t, sex='Female'), lc.get_death_rate(t, sex='Male')
    dr_f, dr_m = pd.Series(dr_f), pd.Series(dr_m)

    d_f, d_m = dr_f * n_f, dr_m * n_m

    brs = lc.get_birth_rate(t)

    n_f, n_m = n_f.sum(), n_m.sum()
    d_f, d_m = f * d_f.sum() / n_f, m * d_m.sum() / n_m

    n_all = n_f + n_m

    return [
        n_all * brs['Female'] - d_f,
        n_all * brs['Male'] - d_m
    ]


ctrl = cx.Director()
ctrl.load_bayes_net('scripts/pSIR.txt')

bp = ctrl.new_sim_model('EBM SIR', 'ODEEBM')
bp.set_fn_ode(SIR_ODE, ['F', 'M'])
bp.set_external_variables({'life': dlc})
bp.set_dt(dt=0.1, odt=1)
bp.set_observations()

model = ctrl.generate_model('M1', 'EBM SIR', bn='pSIR')

y0 = cx.ODEY0()
ns = {k: v.sum() for k, v in dlc.get_population(1990).items()}
y0.define(st='F', n=ns['Female'])
y0.define(st='M', n=ns['Male'])

out = cx.simulate(model, y0, 1990, 2020, 1, log=False)

out.plot()
plt.show()
