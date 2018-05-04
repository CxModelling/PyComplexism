__author__ = 'TimeWz667'
__all__ = ['Event']


class Event:
    NullEvent = None

    def __init__(self, todo, ti):
        """
        To do something at a certain time
        :param todo: a thing to do
        :param ti: a certain time for the event
        """
        self.Time = ti
        self.Todo = todo

    def __call__(self, *args, **kwargs):
        return self.Todo

    def __gt__(self, ot):
        return self.Time > ot.Time

    def __le__(self, ot):
        return self.Time <= ot.Time

    def __eq__(self, ot):
        return self.Time == ot.Time

    def __repr__(self):
        return 'Event(Todo: {}, Time: {})'.format(self.Todo, self.Time)

    def __str__(self):
        return '{}: {}'.format(self.Todo, self.Time)


Event.NullEvent = Event('Nothing', float('inf'))
