import complexism as cx
import epidag as dag

__author__ = 'TimeWz667'

# Create a new blueprint of CTMC
bp = cx.BlueprintCTMC('Test')

# Add a new state
bp.add_state('A')
print('\nStates:')
print(bp.States)

# Add transitions
bp.add_transition('TrAB', 'B')
bp.add_transition('TrBC', 'C')
bp.add_transition('TrCA', 'A')
print('\nTransitions:')
print(bp.Transitions)

bp.link_state_transition('A', 'TrAB')
bp.link_state_transition('B', 'TrBC')
bp.link_state_transition('C', 'TrCA')
print('\nLinks between states and transitions')
print(bp.Targets)


# Now use script to construct pcore

psc = """
PCore ABC{
    beta ~ exp(0.5)
    TrAB ~ lnorm(beta, 1)
    TrBC ~ gamma(beta, 100)
    TrCA ~ k(100)
}
"""

# Sample root nodes
pc = dag.quick_build_parameter_core(psc)
print('\nUse a parameter model to support samplers')
print(pc.Actors.keys())
# Use pc to generate a dynamic core
dc = bp.generate_model('Test1', **pc.Actors)
print('\nCombining parameter model and dynamic model')
print(dc)


state_a = dc['A']
print('\nTake a state from the dynamicmodel')
print(state_a)

print('\nUpcoming transitions')
print(state_a.next_transitions())
