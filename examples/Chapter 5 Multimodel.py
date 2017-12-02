from dzdy import *

__author__ = 'TimeWz667'

pc = """
PCore pSIR{
    transmission_rate ~ unif(0.005, 0.007)
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
hu.add_behaviour('Out', 'Multiplier', t_tar='Infect')
# hu.add_behaviour('In', 'InfectionDD', t_tar='Infect', s_src='Inf')
hu.set_observations(states=['Inf'],
                    transitions=['Infect'], behaviours=['Out'])
hu.set_arguments('fdt', 0.01)
hu.set_arguments('dt', 0.1)


lyo = da.new_layout('Flu')
lyo.add_entry('A', 'SIR', {'Sus': 100})
lyo.add_entry('B', 'SIR', {'Sus': 95, 'Inf': 5}, size=2)

lyo.add_relation('*@Inf', 'Flu@FOI')
lyo.add_relation('Flu@FOI', '*@Out')
lyo.add_relation('B_0@Infect', 'Flu@')
lyo.add_relation('B_1@Infect', 'Flu@')
lyo.add_relation('#A@Out', 'Flu@')

lyo.set_observations(['*'])

#flu.link(RelationEntry('B@Inf'), RelationEntry('A@Out'))

mod, out = da.simulate('Flu', fr=0, to=5, fixed=[])
print(out)

for m in mod.Models.values():
    print(m.PCore)
