import complexism as cx
import epidag as dag

__author__ = 'TimeWz667'

# Create a new blueprint of CTBN
bp = cx.BlueprintCTBN('Test')

# Add microstates
bp.add_microstate('A', ['N', 'Y'])
bp.add_microstate('B', ['N', 'Y'])

# Name combinations of microstates as states
bp.add_state('A', A='Y')
bp.add_state('a', A='N')
bp.add_state('B', B='Y')
bp.add_state('b', B='N')
bp.add_state('ab', A='N', B='N')
bp.add_state('AB', A='Y', B='Y')

# Add transitions
bp.add_transition('TrA', 'A', 'exp(0.1)')
bp.add_transition('TrB', 'B')

# Link transitions to states
bp.link_state_transition('a', 'TrA')
bp.link_state_transition('b', 'TrB')


psc = """
PCore ABC{
    beta ~ exp(0.5)
    TrA ~ lnorm(beta, 1)
    TrB ~ gamma(beta, 100)
}
"""

# Sample root nodes
pc = dag.quick_build_parameter_core(psc)
print('\nUse a parameter model to support samplers')
print(pc.Actors.keys())
# Use pc to generate a dynamic core
dc = bp.generate_model('TestCTBN', **pc.Actors)
print('\nCombining parameter model and dynamic model')
print(dc)

state_ab = dc['ab']
state_a = dc['a']
state_A = dc['A']

print('\nTest inclusions')
# print('ab have a:', state_ab.isa(state_a))
print('ab have a:', state_a in state_ab)
print('ab have A:', state_A in state_ab)

print('\nTransitions follows ab')
print(state_ab.next_transitions())
