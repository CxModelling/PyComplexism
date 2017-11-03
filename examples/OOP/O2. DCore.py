from dzdy.dcore import *
from epidag import DirectedAcyclicGraph

__author__ = 'TimeWz667'

# Generate a new parameter core
script = """
PCore ABC{
    beta ~ exp(0.5)
    TrAB ~ lnorm(beta, 1)
    TrBC ~ gamma(beta, 100)
    TrCA ~ k(100)
}
"""

sm = DirectedAcyclicGraph(script).get_simulation_model()
pc = sm.sample_core()


print('Open a new blueprint of Continuous-Time Markov Chain')
bp = BlueprintCTMC('Test')
print(bp)
print()

print('Define a new state A')
bp.add_state('A')
print(bp.States)
print()

print('Define transitions, mentioned state will be added if it does not exist')
bp.add_transition('TrAB', 'B')
bp.add_transition('TrBC', 'C')
bp.add_transition('TrCA', 'A')
print(bp.Transitions)
print()

print('Assign transitions to their sources')
bp.link_state_transition('A', 'TrAB')
bp.link_state_transition('B', 'TrBC')
bp.link_state_transition('C', 'TrCA')
print(bp.Targets)
print()


print('Complete blueprint')
print(bp)
print()

# print('MC')
mc = bp.generate_model(pc)

print('Get a state from the dynamic model')
StateA = mc['A']
print(StateA)
print('Available transitions')
print(StateA.next_transitions())
