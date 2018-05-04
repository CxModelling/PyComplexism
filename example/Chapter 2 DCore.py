import complexism as cx
import complexism.misc as misc
import epidag as dag

__author__ = 'TimeWz667'


bp = cx.BlueprintCTMC('Test')
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
    TrAB ~ lnorm(beta, 1)
    TrBC ~ gamma(beta, 100)
    TrCA ~ k(100)
}
"""

# Get blueprint of simulation core
bn = dag.bn_from_script(script)
sm = dag.as_simulation_core(bn)

# Sample root nodes
pc = sm.generate('pc')
print(pc.Actors.keys())
# Use pc to generate a dynamic core
dc = bp.generate_model('Test1', **pc.Actors)

print(dc)

print(dc.States)

state_a = dc['A']
print(state_a)

print(state_a.next_transitions())

dc = cx.read_dc(misc.load_txt('scripts/BAD.txt'))

print(dc)
