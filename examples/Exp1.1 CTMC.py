from dzdy.dcore import *

__author__ = 'TimeWz667'

psc = """
    {
        TrAB ~ k(4)
        TrBC ~ gamma(0.01, 100)
        TrCA ~ k(100)
    }
    """

bp_test = BluePrintCTMC('Test', psc)
print(bp_test.to_json())

bp_test.add_state('A')
print(bp_test.States)

bp_test.add_transition('TrAB', 'B')
bp_test.add_transition('TrBC', 'C')
bp_test.add_transition('TrCA', 'A')
print(bp_test.Transitions)

bp_test.link_state_transition('A', 'TrAB')
bp_test.link_state_transition('B', 'TrBC')
bp_test.link_state_transition('C', 'TrCA')
print(bp_test.Targets)

print(bp_test.to_json())
md_test = bp_test.generate_model()
state_test = md_test['A']
evt_test = state_test.next_event()
print(repr(state_test))
print(evt_test)

print(state_test.next_transitions())
print(state_test.next_events())
while evt_test.Time < 200:
    print(evt_test.Time)
    state_test = state_test.exec(evt_test.Transition)
    evt_test = state_test.next_event(evt_test.Time)
    print(state_test)
    print(evt_test)