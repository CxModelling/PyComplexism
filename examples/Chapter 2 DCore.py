from dzdy.dcore import *
from epidag import DirectedAcyclicGraph

__author__ = 'TimeWz667'


bp = BlueprintCTMC('Test')
print(bp.to_json())

bp.add_state('A')
print(bp.States)

bp.add_transition('TrAB', 'B')
bp.add_transition('TrBC', 'C')
bp.add_transition('TrCA', 'A')
print(bp.Transitions)

bp.link_state_transition('A', 'TrAB')
bp.link_state_transition('B', 'TrBC')
bp.link_state_transition('C', 'TrCA')
print(bp.Targets)


# Now use script to construct pcore

script = """
PCore ABC{
    beta ~ exp(0.5)
    TrAB ~ lognorm(beta, 1)
    TrBC ~ gamma(beta, 100)
    TrCA ~ k(100)
}
"""

# Get blueprint of simulation core
sm = DirectedAcyclicGraph(script).get_simulation_model()

# Sample root nodes
pc = sm.sample_core()

# Use pc to generate a dynamic core
dc = bp.generate_model(pc, 'Test1')

print(dc)

print(dc.States)

state_a = dc['A']
print(state_a)

print(state_a.next_transitions())
