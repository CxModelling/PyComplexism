from dzdy.dcore import *

__author__ = 'TimeWz667'

dc_script = '''
CTBN SIR_scr{

    life[Alive | Dead]
    sir[S | I | R]

    Alive{life:Alive}
    Dead{life:Dead}
    Inf{life:Alive, sir:I}
    Rec{life:Alive, sir:R}
    Sus{life:Alive, sir:S}

    Die -> Dead # from transition Die to state Dead by distribution Die
    Infect(beta) -> Inf
    Recov(gamma) -> Rec

    Alive -- Die # from state Alive to transition Die
    Sus -- Infect
    Inf -- Recov
}
'''

# build cd from script
dc = build_from_script(dc_script)
print(dc)



