from collections import namedtuple, OrderedDict

__author__ = 'TimeWz667'


SingleEntry = namedtuple('SingleEntry', ('Prototype', 'Y0'))
MultipleEntry = namedtuple('MultipleEntry', ('Prototype', 'Y0', 'Index'))


class ModelLayout:
    def __init__(self, name):
        self.Name = name
        self.Entries = OrderedDict()

    def append(self, chd):
        pass

    def add_entry(self, name, proto, y0, **kwargs):
        index = None
        if 'index' in kwargs:
            index = kwargs['index']
        elif 'size' in kwargs:
            if 'fr' in kwargs:
                index = range(kwargs['fr'], kwargs['size']+kwargs['fr'])
            else:
                index = range(kwargs['size'])
        elif 'fr' in kwargs and 'to' in kwargs:
            if 'by' in kwargs:
                index = range(kwargs['fr'], kwargs['to'] + 1, step=kwargs['by'])
            else:
                index = range(kwargs['fr'], kwargs['to'] + 1)

        if index:
            self.Entries[name] = MultipleEntry(proto, y0, index)
        else:
            self.Entries[name] = SingleEntry(proto, y0)
