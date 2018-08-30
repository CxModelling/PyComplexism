import re

__author__ = 'TimeWz667'


class SingleEntry:
    def __init__(self, name, proto, y0):
        self.Name = name
        self.Prototype = proto
        self.Y0 = y0

    def __repr__(self):
        return 'Model: {}, Prototype: {}'.format(self.Name, self.Prototype)

    def gen(self):
        yield self.Name, self.Prototype, self.Y0

    def to_json(self):
        return {
            'Name': self.Name,
            'Prototype': self.Prototype,
            'Y0': self.Y0
        }

    @staticmethod
    def from_json(js):
        ent = js['Name'], js['Prototype'], js['Y0']
        return SingleEntry(*ent)


class MultipleEntry:
    def __init__(self, name, proto, y0, index):
        self.Name = name
        self.Prototype = proto
        self.Y0 = y0
        self.Index = index

    def __repr__(self):
        return 'Model: {}, Prototype: {}'.format(self.Name, self.Prototype)

    def gen(self):
        if 'index' in self.Index:
            index = self.Index['index']
        elif 'size' in self.Index:
            if 'fr' in self.Index:
                index = range(self.Index['fr'], self.Index['size']+self.Index['fr'])
            else:
                index = range(self.Index['size'])
        elif 'fr' in self.Index and 'to' in self.Index:
            if 'by' in self.Index:
                index = range(self.Index['fr'], self.Index['to'] + 1, step=self.Index['by'])
            else:
                index = range(self.Index['fr'], self.Index['to'] + 1)
        else:
            raise IndexError('No             matched index pattern')

        for i in index:
            yield '{}_{}'.format(self.Name, i), self.Prototype, self.Y0

    def to_json(self):
        return {
            'Name': self.Name,
            'Prototype': self.Prototype,
            'Y0': self.Y0,
            'Index': self.Index
        }

    @staticmethod
    def from_json(js):
        ent = js['Name'], js['Prototype'], js['Y0'], js['Index']
        return MultipleEntry(*ent)


class RelationEntry:
    def __init__(self, val, parse=True):
        self.Selector, self.Single, self.Parameter = RelationEntry.parse(val) if parse else val

    def __repr__(self):
        return 'Selector: {}, Type: {}, Parameter: {}'.format(self.Selector, self.type(), self.Parameter)

    def is_single(self):
        return self.Single

    def indicator(self):
        return '{}@{}'.format(self.Selector, self.Parameter)

    def type(self):
        return 'Single' if self.Single else 'Multiple'

    def to_json(self):
        return {
            'Selector': self.Selector,
            'Type': self.type(),
            'Parameter': self.Parameter
        }

    @staticmethod
    def from_json(js):
        ent = js['Selector'], js['Type'] is 'Single', js['Parameter']
        return RelationEntry(ent, parse=False)

    @staticmethod
    def parse(ori):
        s = re.sub(r'\s+', '', ori)
        try:
            sel, par = s.split('@', 1)
            if re.match('\A\w+\Z', sel):
                return sel, True, par
            else:
                return sel, False, par
        except ValueError:
            raise SyntaxError('Ill-defined selector')
