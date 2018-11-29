import complexism as cx
import pandas as pd
import matplotlib.pyplot as plt

__author__ = 'TimeWz667'


mat = pd.read_csv('../data/SimFM.csv')

ds = cx.DemographySex()
ds.load_birth_data(mat, i_year='Year', i_f='BirthF', i_m='BirthM')
ds.load_death_data(mat, i_year='Year', i_f='DeathF', i_m='DeathM')
ds.load_migration_data(mat, i_year='Year', i_f='MigrationF', i_m='MigrationM')
ds.load_population_data(mat, i_year='Year', i_f='PopF', i_m='PopM')
ds.complete_loading()


def SIR_ODE(y, t, p, x):
    life = x['life']
    f = y[0]
    m = y[1]

    brs = life.get_birth_rate(t)
    mrs = life.get_migration_rate(t)
    drs = life.get_death_rate(t)

    return [
        f * (brs['Female'] - drs['Female'] + mrs['Female']),
        m * (brs['Male'] - drs['Male'] + mrs['Male'])
    ]


ctrl = cx.Director()
ctrl.load_bayes_net('scripts/pSIR.txt')

bp = ctrl.new_sim_model('EBM SIR', 'ODEEBM')
bp.set_fn_ode(SIR_ODE, ['F', 'M'])
bp.set_external_variables({'life': ds})
bp.set_dt(dt=0.1, odt=1)
bp.set_observations()

model = ctrl.generate_model('M1', 'EBM SIR', bn='pSIR')

y0 = cx.ODEY0()
ns = {k: v.sum() for k, v in ds.get_population(1990).items()}
y0.define(st='F', n=ns['Female'])
y0.define(st='M', n=ns['Male'])

out = cx.simulate(model, y0, 1990, 2050, 1, log=False)

out.plot()
plt.show()
