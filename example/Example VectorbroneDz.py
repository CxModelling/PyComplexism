from dzdy import *

__author__ = 'TimeWz667'

pc_h = """
PCore pH{
    transmission_rate = 0.005
    beta ~ exp(transmission_rate)
    gamma ~ exp(0.5)
}
"""

dc_h = """
CTMC SIR_H{
    Sus
    Inf
    Rec
    Sus -- Infect(beta) -> Inf
    Inf -- Recov(gamma) -> Rec
}
"""

pc_m = """
PCore pM{
    transmission_rate = 0.35
    beta ~ exp(1.5)
    gamma ~ exp(0.2)
}
"""

dc_m = """
CTMC SIS_M{
    Sus
    Inf
    Rec
    Sus -- Infect(beta) -> Inf
    Inf -- Recov(gamma) -> Rec
}
"""

da = Director()
da.read_pc(pc_h)
da.read_pc(pc_m)
da.read_dc(dc_h)
da.read_dc(dc_m)

hu = da.new_mc('Human', 'ABM', tar_pc='pH', tar_dc='SIR_H')
hu.add_behaviour('FOI', 'ForeignShock', t_tar='Infect')
hu.set_observations(states=['Sus', 'Inf'], behaviours=['FOI'])

mo = da.new_mc('Mos', 'ABM', tar_pc='pM', tar_dc='SIS_M')
mo.add_behaviour('M2M', 'ComFDShock', s_src='Inf', t_tar='Infect')
mo.set_observations(states=['Sus', 'Inf'], behaviours=['M2M'])

den = ModelSet('Den', odt=0.25)
den.append(da.generate_model('Human'))
den.append(da.generate_model('Mos'))

den.link('Mos@Inf', 'Human@FOI')

den.add_obs_model('Mos')
den.add_obs_model('Human')
# den.add_obs_model('*')

simulate(den, y0={'Human':{'Sus': 100}, 'Mos':{'Sus': 15, 'Inf': 5}}, fr=0, to=10)
den.Obs.print()
