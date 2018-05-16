import matplotlib.pyplot as plt
from numpy.random import choice
import complexism as cx
from complexism.element import Event


__author__ = 'TimeWz667'


# Step 1 set a parameter core


# Step 2 define at least one type of agent
class TwoDRandomWalker(cx.GenericAgent):
    def update_time(self, time):
        self['t'] = time

    def __init__(self, name):
        cx.GenericAgent.__init__(self, name)

    def find_next(self):
        return Event(todo=(choice([-1, 0, 1]), choice([-1, 0, 1])),
                     ti=self['t'] + self['dt'])

    def initialise(self, time=0, **kwargs):
        self['t'] = time
        self['dt'] = kwargs['dt'] if 'dt' in kwargs else 1
        self['x'] = kwargs['x'] if 'x' in kwargs else 0
        self['y'] = kwargs['y'] if 'y' in kwargs else 0

    def reset(self, time=0, *args, **kwargs):
        self['x'] = kwargs['x'] if 'x' in kwargs else 0
        self['y'] = kwargs['y'] if 'y' in kwargs else 0
        self['t'] = time

    def execute_event(self):
        evt = self.Next
        dx, dy = evt.Todo
        self['x'] += dx
        self['y'] += dy

    def clone(self, *args, **kwargs):
        pass


# Step 3 generate a model
ag = TwoDRandomWalker('Helen')
model = cx.SingleIndividualABM('M1', ag)

# Step 4 decide outputs
for at in ['x', 'y']:
    model.add_observing_attribute(at)

# Step 5 simulate
output = cx.simulate(model, None, 0, 10, 1)

# Step 6 inference, draw figures, and manage outputs
print(output)
output.plot()
plt.show()
