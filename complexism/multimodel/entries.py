from complexism.mcore import ImpulseChecker, ImpulseResponse, get_impulse_response, get_impulse_checker

__author__ = 'TimeWz667'
__all__ = ['SingleEntry', 'MultipleEntry', 'InteractionEntry']


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


class InteractionEntry:
    def __init__(self, sel, checker, response):
        self.Selector = sel
        if isinstance(checker, ImpulseChecker):
            self.Checker = checker
        elif callable(checker):
            self.Checker = checker
        else:
            try:
                self.Checker = get_impulse_checker(checker['Type'], **checker)
            except KeyError or AttributeError:
                raise TypeError('Unknown type of impulse checker')

        if isinstance(response, ImpulseResponse):
            self.Response = response
        elif callable(response):
            self.Response = response
        else:
            try:
                self.Response = get_impulse_response(response['Type'], **response)
            except KeyError or AttributeError:
                raise TypeError('Unknown type of impulse response')

    def to_json(self):
        return {
            'Selector': self.Selector,
            'Checker': self.Checker.to_json(),
            'Response': self.Response.to_json()
        }

    def pass_checker(self):
        try:
            return self.Checker.clone()
        except AttributeError as e:
            if callable(self.Checker):
                return self.Checker
            else:
                raise e

    def pass_response(self):
        try:
            return self.Response.clone()
        except AttributeError as e:
            if callable(self.Response):
                return self.Response
            else:
                raise e

    @staticmethod
    def from_json(js):
        return InteractionEntry(js['Selector'], js['Checker'], js['Response'])


class SummaryEntry:
    def __init__(self, sel, key, name=None):
        self.Selector = sel
        self.Key = key
        self.NewName = name if name else '{}@{}'.format(sel, key)

    def __repr__(self):
        return 'Task({}@{}->{})'.format(self.Selector, self.Key, self.NewName)

    def to_json(self):
        return {
            'Selector': self.Selector,
            'Key': self.Key,
            'NewName': self.NewName
        }

    @staticmethod
    def from_json(js):
        ent = js['Selector'], js['Key'], js['NewName']
        return SummaryEntry(*ent)
