from dzdy.dcore import *

__author__ = 'TimeWz667'

psc = """
    {
        Infect ~ exp(0.4)
        Recov ~ exp(0.2)
        Die ~ exp(0.02)
    }
    """

bp_test = BluePrintCTBN('SIR', psc)
bp_test.add_microstate('sir', ['S', 'I', 'R'])
bp_test.add_microstate('life', ['Alive', 'Dead'])

bp_test.add_state('Sus', sir='S', life='Alive')
bp_test.add_state('Inf', sir='I', life='Alive')
bp_test.add_state('Rec', sir='R', life='Alive')
bp_test.add_state('Alive', life='Alive')
bp_test.add_state('Dead', life='Dead')
bp_test.add_transition('Infect', 'Inf')
bp_test.add_transition('Recov', 'Rec')
bp_test.add_transition('Die', 'Dead')
bp_test.link_state_transition('Sus', 'Infect')
bp_test.link_state_transition('Inf', 'Recov')
bp_test.link_state_transition('Alive', 'Die')

md_test = bp_test.generate_model()
print(md_test)

state_test = md_test['Sus']
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
