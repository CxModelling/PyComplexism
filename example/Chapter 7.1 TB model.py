import complexism as cx
import pandas as pd
import numpy as np
import numpy.random as rd

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
    sus_f, sus_m, flat_f, flat_m, slat_f, slat_m, rec_f, rec_m = y

    n = y.sum() + x['N_abm']
    n_f = sus_f + flat_f + slat_f + rec_f
    n_m = sus_m + flat_m + slat_m + rec_m

    foi = x['Inf'] * p['r_tr'] / n

    life = x['life']
    brs = life.get_birth_rate(t)
    mrs = life.get_migration_rate(t)
    drs = life.get_death_rate(t)
    in_f = mrs['Female'] - drs['Female']
    in_m = mrs['Male'] - drs['Male']

    dy = [
        n_f * brs['Female'] + sus_f * (foi + in_f),
        n_m * brs['Male'] + sus_m * (foi + in_m),
        sus_f * foi + flat_f * (- p['r_slat'] + in_f),
        sus_m * foi + flat_m * (- p['r_slat'] + in_m),
        flat_f * p['r_slat'] + slat_f * in_f,
        flat_m * p['r_slat'] + slat_m * in_m,
        rec_f * in_f,
        rec_m * in_m
    ]

    return np.array(dy)


def TB_Measure(y, t, p, x):
    ne = y.sum()
    return {
        'N_ebm': ne,
        'Sus': y[0] + y[1],
        'FLat': y[2] + y[3],
        'SLat': y[4] + y[5],
        'Rec': y[6] + y[7],
        'N': ne + x['N_abm']
    }


class InfIn(cx.ImpulseResponse):
    def __init__(self):
        self.Last = None

    def initialise(self, ti):
        self.Last = ti

    def __call__(self, disclosure, model_foreign, model_local, ti):
        if self.Last:
            dt = ti - self.Last
            self.Last = ti
            if dt > 0:
                r_act = model_local.get_parameter('r_act')
                act_f = self.__calculate_birth_number(model_foreign.Y['LatFastF'], r_act, dt)
                act_m = self.__calculate_birth_number(model_foreign.Y['LatFastM'], r_act, dt)

                model_local.shock(ti, 'ActIn', n=act_f, Type='Activation', Sex='Female')
                model_local.shock(ti, 'ActIn', n=act_m, Type='Activation', Sex='Male')

                r_ract = model_local.get_parameter('r_ract')
                ract_f = self.__calculate_birth_number(model_foreign.Y['LatSlowF'], r_ract, dt)
                ract_m = self.__calculate_birth_number(model_foreign.Y['LatSlowM'], r_ract, dt)

                model_local.shock(ti, 'ActIn', n=ract_f, Type='Reactivation', Sex='Female')
                model_local.shock(ti, 'ActIn', n=ract_m, Type='Reactivation', Sex='Male')

                r_rel = model_local.get_parameter('r_rel')
                rel_f = self.__calculate_birth_number(model_foreign.Y['RecF'], r_rel, dt)
                rel_m = self.__calculate_birth_number(model_foreign.Y['RecM'], r_rel, dt)

                model_local.shock(ti, 'ActIn', n=rel_f, Type='Relapse', Sex='Female')
                model_local.shock(ti, 'ActIn', n=rel_m, Type='Relapse', Sex='Male')
                print(ti)
                # print(act_f+ract_f+rel_f)
                # return 'ActIn', {'n': act_f, }
        else:
            self.Last = ti

    def __calculate_birth_number(self, n, rate, dt):
        n = np.floor(n)
        if n <= 0:
            return 0
        lam = rate * n * dt
        if lam < 5:
            nb = rd.poisson(lam)
        else:
            nb = rd.binomial(n, - np.expm1(-rate * dt))
        return min(nb, n)


class ToRecImpulse(cx.ImpulseResponse):
    def __call__(self, disclosure, model_foreign, model_local, ti):
        if disclosure['Sex'] == 'Female':
            return 'add', {'y': 'RecF', 'n': 1}
        else:
            return 'add', {'y': 'RecM', 'n': 1}


ctrl = cx.Director()
ctrl.load_bayes_net('scripts/tb/ptb.txt')
ctrl.load_state_space_model('scripts/tb/dtb_cases.txt')
ctrl.list_bayes_nets(), ctrl.list_state_spaces()

# ABM definition
mbp_i = ctrl.new_sim_model('I', 'StSpABM')
mbp_i.set_agent(prefix='Ag', group='AgI', dynamics='Active')
mbp_i.add_behaviour('Dead', 'CohortLeeCarter', s_death='Dead', t_die='Die', dlc=lcp)
mbp_i.add_behaviour('Recovery', 'Cohort', s_death='PostCare')
mbp_i.add_behaviour('ActIn', 'AgentImport', s_birth='Act')
mbp_i.add_behaviour('StInf', 'StateTrack', s_src='Inf')
mbp_i.set_observations(states=['Alive', 'PreCare', 'InCare'],
                       transitions=['Treat', 'Die', 'Die_TB'],
                       behaviours=['ActIn'])

# EBM definition
mbp_ser = ctrl.new_sim_model('SER', 'ODEEBM')
ys = ['SusF', 'SusM', 'LatFastF', 'LatFastM', 'LatSlowF', 'LatSlowM', 'RecF', 'RecM']
mbp_ser.set_fn_ode(TB_ODE, ys)
mbp_ser.set_external_variables({'Inf': 0, 'N_abm': 0, 'life': ds})
mbp_ser.set_dt(dt=0.05, odt=0.5)
mbp_ser.add_observing_function(TB_Measure)


scale = 0.01
y0_i = mbp_i.get_y0_proto()
y0_i.define(st='Act', n=1)

y0_ser = mbp_ser.get_y0_proto()
ns = {k: v.sum() for k, v in ds.get_population(1990).items()}
y0_ser.define(st='SusF', n=ns['Female'] * 0.75 * scale)
y0_ser.define(st='SusM', n=ns['Male'] * 0.75 * scale)
y0_ser.define(st='LatSlowF', n=ns['Female'] * 0.125 * scale)
y0_ser.define(st='LatSlowM', n=ns['Male'] * 0.125 * scale)
y0_ser.define(st='RecF', n=ns['Female'] * 0.125)
y0_ser.define(st='RecM', n=ns['Male'] * 0.125)


lyo = ctrl.new_sim_model('SEIR', 'MultiModel')
lyo.add_entry('i', 'I', y0_i)
lyo.add_entry('ser', 'SER', y0_ser)

lyo.add_interaction('ser',
                    cx.WhoStartWithChecker('StInf', 'update value'),
                    cx.ValueImpulse('Inf', 'v1'))

lyo.add_interaction('ser',
                    cx.WhoStartWithChecker('Recovery', 'remove agent'),
                    ToRecImpulse())

lyo.add_interaction('ser',
                    cx.StartsWithAndMatchesChecker('add', {'Type': 'Activation', 'Sex': 'Female'}),
                    cx.MinusNImpulse('LatFastF', 'n'))

lyo.add_interaction('ser',
                    cx.StartsWithAndMatchesChecker('add', {'Type': 'Activation', 'Sex': 'Male'}),
                    cx.MinusNImpulse('LatFastM', 'n'))

lyo.add_interaction('ser',
                    cx.StartsWithAndMatchesChecker('add', {'Type': 'Reactivation', 'Sex': 'Female'}),
                    cx.MinusNImpulse('LatSlowF', 'n'))

lyo.add_interaction('ser',
                    cx.StartsWithAndMatchesChecker('add', {'Type': 'Reactivation', 'Sex': 'Male'}),
                    cx.MinusNImpulse('LatSlowM', 'n'))

lyo.add_interaction('ser',
                    cx.StartsWithAndMatchesChecker('add', {'Type': 'Relapse', 'Sex': 'Female'}),
                    cx.MinusNImpulse('RecF', 'n'))

lyo.add_interaction('ser',
                    cx.StartsWithAndMatchesChecker('add', {'Type': 'Relapse', 'Sex': 'Male'}),
                    cx.MinusNImpulse('RecM', 'n'))

lyo.add_interaction('i', cx.IsChecker('update'), InfIn())

lyo.set_observations()


model = ctrl.generate_model('M1', 'SEIR', bn='pTB')

y0 = ctrl.get_y0s('SEIR')
cx.start_counting()
out = cx.simulate(model, y0, 1990, 2000, 1, log=False)
cx.stop_counting()
print(out)
print(cx.get_counting_results())

