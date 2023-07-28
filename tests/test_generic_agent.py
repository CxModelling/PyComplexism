import unittest
import complexism as cx
from element import Event
from random import choice


class TwoDRandomWalker(cx.GenericAgent):
    def update_time(self, time):
        self['t'] = time

    def __init__(self, name):
        cx.GenericAgent.__init__(self, name)

    def find_next(self):
        return Event((choice([-1, 0, 1]), choice([-1, 0, 1])), self['t'] + self['dt'])

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


class GenericAgentTestCase(unittest.TestCase):
    def setUp(self):
        self.Walker = TwoDRandomWalker('Helen')

    def test_creation(self):
        self.Walker.initialise(time=1, dt=0.5)
        self.assertEqual(self.Walker['t'], 1)
        self.assertEqual(self.Walker['dt'], 0.5)

        self.Walker.initialise(time=1, dt=0.5, x=1, y=1)
        self.assertEqual(self.Walker['x'], 1)
        self.assertEqual(self.Walker['y'], 1)

        evt = self.Walker.Next
        self.assertEqual(evt.Time, 1.5)
        self.assertIn(evt.Todo[0], [-1, 0, 1])

        dx, dy = evt.Todo

        self.Walker.execute_event()
        self.assertEqual(self.Walker.Next, evt)
        self.assertEqual(self.Walker['x'], 1+dx)
        self.assertEqual(self.Walker['y'], 1+dy)
        self.assertEqual(self.Walker['t'], 1)

        self.Walker.drop_next()

        self.Walker.update_time(evt.Time)
        self.assertFalse(self.Walker.Next is evt)
        self.assertEqual(self.Walker.TTE, 2)


if __name__ == '__main__':
    unittest.main()
