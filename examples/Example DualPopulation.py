from dzdy import *

__author__ = 'TimeWz667'

pc = """
PCore pSIR{
    transmission_rate = 0.005
    betaO ~ exp(transmission_rate/100)
    betaI ~ exp(transmission_rate)
    gamma ~ exp(0.5)
}
"""

dc = """
CTMC SIR{
    Sus
    Inf
    Rec
    Sus -- InfI(betaI) -> Inf
    Sus -- InfO(betaO) -> Inf
    Inf -- Recov(gamma) -> Rec
}
"""

da = Director()
da.read_pc(pc)
da.read_dc(dc)


hu = da.new_mc('SIR', 'CoreODE', tar_pc='pSIR', tar_dc='SIR')
hu.add_behaviour('Out', 'Multiplier', t_tar='InfO')
hu.add_behaviour('In', 'InfectionDD', t_tar='InfI', s_src='Inf')
hu.set_observations(states=['Inf'],
                    transitions=['InfO', 'InfI'])
hu.set_arguments('fdt', 0.01)


flu = DualModel('Flu', odt=0.05)
flu.append(da.generate_model('SIR', name='A'))
flu.append(da.generate_model('SIR', name='B'))

flu.link(RelationEntry('A@P_Inf'), RelationEntry('B@Out'))
flu.link(RelationEntry('B@P_Inf'), RelationEntry('A@Out'))

simulate(flu, y0={'A':{'Sus': 100}, 'B':{'Sus': 15, 'Inf': 5}}, fr=0, to=10)
flu.Obs.print()
