from dzdy import *

__author__ = 'TimeWz667'


pc = """
PCore pSIR{
    transmission_rate = 0.005
    beta ~ exp(transmission_rate)
    gamma ~ exp(0.5)
}
"""

dc = """
CTMC SIR{
    Sus
    Inf
    Rec
    Sus -- Infect(beta) -> Inf
    Inf -- Recov(gamma) -> Rec
}
"""

da = Director()
da.read_pc(pc)
da.read_dc(dc)


hu = da.new_mc('SIR', 'CoreODE', tar_pc='pSIR', tar_dc='SIR')
hu.add_behaviour('In', 'InfectionDD', t_tar='Infect', s_src='Inf')
hu.set_observations(states=['Inf'], transitions=['Infect'])
hu.set_arguments('fdt', 0.01)
hu.set_arguments('dt', 0.1)

_, out = da.simulate('SIR', y0={'Sus': 15, 'Inf': 5}, fr=0, to=10)
print(out)


da.load_pc('scripts/pBAD.txt')
da.load_dc('scripts/BAD.txt')

demo = DemographySimplified('../Data/Life_All.csv')

hu = da.new_mc('BAD', 'CoreODE', tar_pc='pBAD', tar_dc='BAD')
hu.add_behaviour('Life', 'DemoDynamic', s_death='Dead', s_birth='Young', t_death='Die', demo=demo)
hu.set_observations(states=['Alive'], transitions=['Die'])
hu.set_arguments('fdt', 0.01)
hu.set_arguments('dt', 0.1)

_, out = da.simulate('BAD', y0={'Young': 100, 'Middle': 100}, fr=0, to=10)
print(out)

