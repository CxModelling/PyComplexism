from dzdy.dcore import *
import epidag

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

