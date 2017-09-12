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
    Sus -- Infect(beta) -> Inf
    Inf -- Recov(gamma) -> Sus
}
"""

da = Director()
da.read_pc(pc_h)
da.read_pc(pc_m)
da.read_dc(dc_h)
da.read_dc(dc_m)

hu = da.new_mc('Human', 'ABM', tar_pc='pH', tar_dc='SIR_H')
hu.set_observations(states=['Sus', 'Inf'])

mo = da.new_mc('Mos', 'ABM', tar_pc='pM', tar_dc='SIS_M')
mo.add_behaviour('M2M', 'ComFDShock', s_src='Inf', t_tar='Infect')
mo.set_observations(states=['Sus', 'Inf'], transitions=['Infect'])

den = DualModel('Den')
den.append(da.generate_model('Human'))
den.append(da.generate_model('Mos'))
den.link(RelationEntry('Mos@P_Inf'), RelationEntry('Human@Infect'))

simulate(den, y0={'Human':{'Sus': 100}, 'Mos':{'Sus': 20, 'Inf': 20}} ,fr=0, to=10)
den.Obs.print()


