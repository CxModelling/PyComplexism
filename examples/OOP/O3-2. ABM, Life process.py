from dzdy import *
from epidag import DirectedAcyclicGraph


__author__ = 'TimeWz667'


# generate a blueprint of PCore
pc_script = """
PCore pLife{
    dr ~ exp(0.1)
}
"""
pc_bp = DirectedAcyclicGraph(pc_script)

# generate a blueprint of DCore
dc_script = """
CTMC Life_mc {
    Alive
    Dead

    Alive -- dr -> Dead
}
"""

dc_bp = build_from_script(dc_script)


# generate a blueprint of MCore
mc_bp = BlueprintABM('Life', 'pLife', 'Life_mc')
mc_bp.add_behaviour('Cohort', 'Cohort', s_death='Dead')
mc_bp.set_observations(states=['Alive', 'Dead'])


# generate a model from the blueprints
pc = pc_bp.get_simulation_model().sample_core()
dc = dc_bp.generate_model(pc=pc)
model = mc_bp.generate('life', pc=pc, dc=dc)

# simulation
out = simulate(model, y0={'Alive': 100}, fr=0, to=10)
print(model.output(mid=False))
