from dzdy import *
from epidag import DirectedAcyclicGraph

__author__ = 'TimeWz667'


# generate a blueprint of PCore
pc_script = """
PCore pAB {
    rB ~ exp(0.1)
    rA0 ~ exp(0.01)
    rA1 ~ exp(0.5)
}
"""
pc_bp = read_pc(pc_script)

# generate a blueprint of DCore
dc_script = """
CTMC AB_mc {
    N
    B
    A
    AB
    N -- toA0(rA0) -> A
    B -- toA1(rA1) -> AB
    N -- toB(rB) -> B
    A -- toB(rB)
}
"""

dc_bp = read_dc(dc_script)


# generate a blueprint of MCore
mc_bp = BlueprintABM('AB_abm', 'pAB', 'AB_mc')
mc_bp.set_observations(states=['N', 'A', 'B', 'AB'])


# generate a model from the blueprints
pc = pc_bp.sample_core()
dc = dc_bp.generate_model(pc=pc)
model = mc_bp.generate('A', pc=pc, dc=dc)

# simulation
out = simulate(model, y0={'N': 500}, fr=0, to=10)
print(model.output(mid=False))
