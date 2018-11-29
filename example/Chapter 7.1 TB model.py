import pandas as pd
import complexism as cx


mat = pd.read_csv('../data/SimFM.csv')

ds = cx.DemographySex()
ds.load_birth_data(mat, i_year='Year', i_f='BirthF', i_m='BirthM')
ds.load_death_data(mat, i_year='Year', i_f='DeathF', i_m='DeathM')
ds.load_migration_data(mat, i_year='Year', i_f='MigrationF', i_m='MigrationM')
ds.load_population_data(mat, i_year='Year', i_f='PopF', i_m='PopM')
ds.complete_loading()


psc = """
PCore pSLIR {
    beta = 0.4
    lambda = 0.2
    gamma = 0.5
    Recov ~ exp(0.5)
    Die ~ exp(0.02)
}
"""

dsc = """
CTBN dIR {
    life[Alive | Dead]
    ir[I | R]

    Alive{life:Alive}
    Dead{life:Dead}
    Inf{life:Alive, ir:I}
    Rec{life:Alive, ir:R}

    Die -> Dead # from transition Die to state Dead by distribution Die
    Inf -- Recov -> Rec

    Alive -- Die # from state Alive to transition Die
}
"""


def SL_ODE(y, t, p, x):
    life = x['life']
    fs, ms, fl, ml = y

    brs = life.get_birth_rate(t)
    mrs = life.get_migration_rate(t)
    drs = life.get_death_rate(t)

    return [
        fs * (brs['Female'] - drs['Female'] + mrs['Female'] - p['lambda']),
        ms * (brs['Male'] - drs['Male'] + mrs['Male'] - p['lambda']),
        fl * (brs['Female'] - drs['Female'] + mrs['Female']) + fs * p['lambda'],
        ml * (brs['Male'] - drs['Male'] + mrs['Male']) + ms * p['lambda']

    ]


ctrl = cx.Director()

ctrl.read_bayes_net(psc)
ctrl.read_state_space_model(dsc)

bp = ctrl.new_sim_model('IR', 'StSpABM')
bp.set_agent('dIR')
bp.set_observations(states=['Inf', 'Rec', 'Dead'])

y0 = bp.get_y0_proto()
y0.define(n=100, st='Inf')

lyo = ctrl.new_sim_model('MIR', 'MultiModel')
lyo.add_entry('M', 'IR', y0, fr=1, to=3)
y0s = lyo.get_y0s()

bp = ctrl.new_sim_model('SL', 'ODEEBM')
bp.set_fn_ode(SL_ODE, ['FS', 'MS', 'FL', 'ML'])
bp.set_external_variables({'life': ds})

bp.set_dt(dt=0.1, odt=1)
bp.set_observations()

lyo = ctrl.new_sim_model('SLIR', 'MultiModel')

y0 = bp.get_y0_proto()
ns = {k: v.sum()/100 for k, v in ds.get_population(1990).items()}
y0.define(st='FS', n=ns['Female'])
y0.define(st='MS', n=ns['Male'])


lyo.add_entry('mir', 'MIR', y0s)
lyo.add_entry('sl', 'SL', y0)


model = ctrl.generate_model('M1', 'SLIR', bn='pSLIR')

y0 = lyo.get_y0s()

out = cx.simulate(model, y0, 1990, 2050, 1, log=False)
print(out)
