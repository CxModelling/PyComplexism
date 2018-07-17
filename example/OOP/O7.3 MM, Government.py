import matplotlib.pyplot as plt
import epidag as dag
import complexism as cx
from complexism.element import ScheduleTicker, Event
import complexism.agentbased as abm
import complexism.agentbased.statespace as ss


class ValuePassing(abm.ActiveBehaviour):
    def __init__(self, name):
        abm.ActiveBehaviour.__init__(self, name, ScheduleTicker(name, ts=[3, 6]), None)

    def compose_event(self, ti):
        return Event('action', self.Clock.Next)

    def do_action(self, model, todo, ti):
        if ti is 3:
            model.get_model('ABM').shock(ti, todo, 'd_rec', 8)
            self.Clock.update(ti)
        elif ti is 6:
            model.get_model('ABM').shock(ti, todo, 'd_rec', 100)
            self.Clock.update(ti)

    def register(self, ag, ti):
        pass

    @staticmethod
    def decorate(name, model, **kwargs):
        pass

    def match(self, be_src, ags_src, ags_new, ti):
        pass


# Step 1 set a parameter core
bn = cx.read_bn_script(cx.load_txt('../scripts/pSIR.txt'))
sm = dag.as_simulation_core(bn,
                            hie={'Country': ['city'],
                                 'city': ['agent'],
                                 'agent': ['Infect', 'Recov', 'Die']})
pc = sm.generate('SIR')


# Step 1- set dynamic cores as agents need
dbp = cx.read_dbp_script(cx.load_txt('../scripts/SIR_BN.txt'))


# Step 2 define at least one type of agent
eve = ss.StSpBreeder('Ag', 'agent', pc.breed('Taipei', 'city'), dbp)
pop = cx.Population(eve)


# Step 3 generate a model
sub_model = cx.StSpAgentBasedModel('ABM', pc, pop)


# Step 4 add behaviours to the model
ss.FDShock.decorate('FOI', sub_model, s_src='Inf', t_tar='Infect')
ss.ExternalShock.decorate('d_rec', sub_model, t_tar='Recov')
ss.Reincarnation.decorate('Life', sub_model, s_death='Dead', s_birth='Sus')

# Step 5 decide outputs
for tr in ['Infect', 'Recov', 'Die']:
    sub_model.add_observing_transition(tr)

for st in ['Sus', 'Inf', 'Rec', 'Alive', 'Dead']:
    sub_model.add_observing_state(st)

sub_model.add_observing_behaviour('FOI')

model = cx.MultiLevelModel('SIR', env=pc)
model.append_actor(ValuePassing('VP'))
model.append(sub_model)


# Step 6 simulate
y0 = {
    'ABM': [
        {'n': 90, 'attributes': {'st': 'Sus'}},
        {'n': 10, 'attributes': {'st': 'Inf'}}
    ]
}


output = cx.simulate(model, y0, 0, 15, 0.5)
print(output)


# Step 7 inference, draw figures, and manage outputs
fig, axes = plt.subplots(nrows=3, ncols=1)

output[['ABM.Sus', 'ABM.Inf', 'ABM.Rec']].plot(ax=axes[0])
output[['ABM.Recov', 'ABM.Infect']].plot(ax=axes[1])
output[['ABM.FOI']].plot(ax=axes[2])
plt.show()
