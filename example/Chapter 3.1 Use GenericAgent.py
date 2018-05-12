import complexism as cx
from complexism.element import Event
from random import choice


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


def step(agent):
    evt = agent.Next
    agent.execute_event()
    agent.drop_next()
    agent.update_time(evt.Time)
    return evt.Time


if __name__ == '__main__':
    ag = TwoDRandomWalker('Helen')
    ag.initialise(0, dt=1)
    print('Agent is in ({}, {})'.format(ag['x'], ag['y']))
    for _ in range(5):
        ti = step(ag)
        print('Time:', ti)
        print('Agent is in ({}, {})'.format(ag['x'], ag['y']))
