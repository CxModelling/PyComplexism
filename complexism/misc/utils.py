__author__ = 'TimeWz667'
__all__ = ['name_generator', 'NameGenerator']


def name_generator(prefix, start, by):
    i = int(start)
    by = int(by) if by >= 1 else by

    while True:
        yield '{}{}'.format(prefix, i)
        i += by


class NameGenerator:
    def __init__(self, prefix, start=0, by=1):
        self.Prefix = prefix
        self.Start = start
        self.By = by
        self.Index = int(start)

    def reset(self):
        self.Index = int(self.Start)

    def get_next(self):
        i, self.Index = self.Index, self.Index + self.By
        return '{}{}'.format(self.Prefix, i)

    def to_json(self):
        return {
            'Prefix': self.Prefix,
            'Start': self.Start,
            'By': self.By
        }

    @staticmethod
    def from_json(js):
        return NameGenerator(js['Prefix'], js['Start'], js['By'])


if __name__ == '__main__':
    ng = NameGenerator('Ag', 1, 1)
    print(ng.get_next())
    print(ng.get_next())
