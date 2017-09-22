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
hu.add_behaviour('Out', 'Multiplier', t_tar='InfO')
hu.add_behaviour('In', 'InfectionDD', t_tar='InfI', s_src='Inf')
hu.set_observations(states=['Inf'],
                    transitions=['InfO', 'InfI'])
hu.set_arguments('fdt', 0.01)
hu.set_arguments('dt', 0.1)


flu = ModelSet('Flu', odt=0.5)
flu.append(da.generate_model('SIR', name='A'))
flu.append(da.generate_model('SIR', name='B'))

flu.link(RelationEntry('*@Inf'), RelationEntry('Flu@FOI'))
flu.link(RelationEntry('B@Inf'), RelationEntry('Flu@'))
flu.link(RelationEntry('A@Inf'), RelationEntry('Flu@'))
#flu.link(RelationEntry('B@Inf'), RelationEntry('A@Out'))

simulate(flu, y0={'A': {'Sus': 100}, 'B': {'Sus': 15, 'Inf': 5}}, fr=0, to=5, dt=1)
flu.Obs.print()
flu.Models['A'].Obs.print()