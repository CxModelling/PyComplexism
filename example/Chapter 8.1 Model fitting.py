import complexism as cx
import pandas as pd
import numpy as np

mat = pd.read_csv('../data/SimFM.csv')

ds = cx.DemographySex()
ds.load_birth_data(mat, i_year='Year', i_f='BirthF', i_m='BirthM')
ds.load_death_data(mat, i_year='Year', i_f='DeathF', i_m='DeathM')
ds.load_migration_data(mat, i_year='Year', i_f='MigrationF', i_m='MigrationM')
ds.load_population_data(mat, i_year='Year', i_f='PopF', i_m='PopM')
ds.complete_loading()


mat_a = pd.read_csv('../data/LCA/LCA.Age.csv')
mat_t = pd.read_csv('../data/LCA/LCA.Time.csv')

mat_bf = pd.read_csv('../data/LCA/BirR.Female.csv')
mat_bm = pd.read_csv('../data/LCA/BirR.Male.csv')

mat_af = pd.read_csv('../data/LCA/PopStart.Female.csv')
mat_am = pd.read_csv('../data/LCA/PopStart.Male.csv')
mat_af = mat_af.fillna(0)
mat_am = mat_am.fillna(0)

lcp = cx.DemographyLeeCarter()

lcp.load_death_female(mat_a, mat_t, i_year='Year', i_age='Age', i_al='ax_f', i_be='bx_f', i_ka='female')
lcp.load_death_male(mat_a, mat_t, i_year='Year', i_age='Age', i_al='ax_m', i_be='bx_m', i_ka='male')

lcp.load_birth_female(mat_bf, i_year='Year', i_rate='br')
lcp.load_birth_male(mat_bm, i_year='Year', i_rate='br')

lcp.load_pop_female(mat_af, i_year='Year', ages=range(0, 101))
lcp.load_pop_male(mat_am, i_year='Year', ages=range(0, 101))

lcp.complete_loading()


def TB_ODE(y, t, p, x):
    sus_f, sus_m, flat_f, flat_m, slat_f, slat_m, inf_f, inf_m, hos_f, hos_m, rec_f, rec_m = y

    n = y.sum()
    n_f = sus_f + flat_f + slat_f + inf_f + hos_f + rec_f
    n_m = sus_m + flat_m + slat_m + inf_m + hos_m + rec_m

    inf = inf_f + inf_m + hos_f + hos_m

    foi = inf * p['r_tr'] / n
    re_foi = (1 - p['partial_immune']) * foi

    t = 1990

    sr_f = np.power(p['rrT'], (t - 1990))/p['delay0']
    sr_m = sr_f * p['rrM']

    ddy = [
        -sus_f * foi,
        -sus_m * foi,
        sus_f * foi + (slat_f+rec_f) * re_foi - flat_f * (p['r_slat'] + p['r_act']),
        sus_m * foi + (slat_m+rec_m) * re_foi - flat_m * (p['r_slat'] + p['r_act']),
        flat_f * p['r_slat'] - slat_f * (p['r_ract'] + re_foi),
        flat_m * p['r_slat'] - slat_m * (p['r_ract'] + re_foi),
        flat_f * p['r_act'] + slat_f * p['r_ract'] + rec_f * p['r_rel'] - inf_f * (p['r_cure'] + sr_f),
        flat_m * p['r_act'] + slat_m * p['r_ract'] + rec_m * p['r_rel'] - inf_m * (p['r_cure'] + sr_m),
        inf_f * sr_f - hos_f * (p['r_cure'] + p['r_treat']),
        inf_m * sr_m - hos_m * (p['r_cure'] + p['r_treat']),
        inf_f * p['r_cure'] + hos_f * (p['r_cure'] + p['r_treat']) - rec_f * (p['r_rel'] + re_foi),
        inf_m * p['r_cure'] + hos_m * (p['r_cure'] + p['r_treat']) - rec_m * (p['r_rel'] + re_foi)
    ]

    # Population dynamics
    life = x['life']
    brs = life.get_birth_rate(t)
    mrs = life.get_migration_rate(t)
    drs = life.get_death_rate(t)
    in_f = mrs['Female'] - drs['Female']
    in_m = mrs['Male'] - drs['Male']

    pdy = [
        n_f * brs['Female'] + sus_f * in_f,
        n_m * brs['Male'] + sus_m * in_m,
        flat_f * in_f,
        flat_m * in_m,
        slat_f * in_f,
        slat_m * in_m,
        inf_f * (in_f - p['r_die_tb']),
        inf_m * (in_m - p['r_die_tb']),
        hos_f * (in_f - p['r_die_tb']),
        hos_m * (in_m - p['r_die_tb']),
        rec_f * in_f,
        rec_m * in_m,
    ]

    return np.array(ddy) + np.array(pdy)


def TB_Measure(y, t, p, x):
    n = y.sum()

    sr_f = np.power(p['rrT'], (t - 1990)) / p['delay0']
    sr_m = sr_f * p['rrM']

    not_f = y[6] * sr_f
    not_m = y[7] * sr_m
    return {
        'Sus': y[0] + y[1],
        'FLat': y[2] + y[3],
        'SLat': y[4] + y[5],
        'Inf': y[6] + y[7],
        'Hos': y[8] + y[9],
        'Rec': y[10] + y[11],
        'Noti': float((not_f + not_m) / n) *1e5,
        'logFM': float(np.log(not_m / not_f)),
        'N': n
    }


ctrl = cx.Director()
ctrl.load_bayes_net('scripts/tb/ptb_fit.txt')


# EBM definition
mbp = ctrl.new_sim_model('SEIR', 'ODEEBM')
ys = ['SusF', 'SusM', 'LatFastF', 'LatFastM', 'LatSlowF', 'LatSlowM', 'InfF', 'InfM', 'HosF', 'HosM', 'RecF', 'RecM']
mbp.set_fn_ode(TB_ODE, ys)
mbp.set_external_variables({'life': ds})
mbp.set_dt(dt=0.05, odt=1)
mbp.add_observing_function(TB_Measure)

y0 = mbp.get_y0_proto()
ns = {k: v.sum() for k, v in ds.get_population(1990).items()}
y0.define(st='SusF', n=ns['Female'] * 0.75)
y0.define(st='SusM', n=ns['Male'] * 0.75)
y0.define(st='LatFastF', n=ns['Female'] * 0.01)
y0.define(st='LatFastM', n=ns['Male'] * 0.01)
y0.define(st='LatSlowF', n=ns['Female'] * 0.114)
y0.define(st='LatSlowM', n=ns['Male'] * 0.114)
y0.define(st='InfF', n=ns['Female'] * 0.001)
y0.define(st='InfM', n=ns['Male'] * 0.001)
y0.define(st='RecF', n=ns['Female'] * 0.125)
y0.define(st='RecM', n=ns['Male'] * 0.125)


model = ctrl.generate_model('M1', 'SEIR', bn='pTB')

cx.start_counting()
out = cx.simulate(model, y0, 0, 200, 1, log=False)
cx.stop_counting()
print(out)
print(cx.get_counting_results())

import matplotlib.pyplot as plt

out[['N']].plot()
plt.show()

