import pandas as pd
import complexism as cx


mat_a = pd.read_csv('../data/LCA/lcA.Age.csv')
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


ctrl = cx.Director()
ctrl.load_bayes_net('scripts/pBD.txt')
ctrl.load_state_space_model('scripts/BD.txt')

abm = ctrl.new_sim_model('BD', 'StSpABM')
abm.set_agent(dynamics='BD', prefix='Ag')
abm.set_observations(states=['Alive'], transitions=['Die'])

abm.add_behaviour('L', 'BirthAgeingDeathLeeCarter', s_death='Dead', t_die='Die', s_birth='Alive', dlc=lcp)

model = ctrl.generate_model('Test', 'BD', bn='pBD')

y0 = [
    {'n': 500, 'attributes': {'st': 'Alive'}}
]


model.add_observing_behaviour("L")
output = cx.simulate(model, y0, 1990, 2020, log=False)
print(output)
