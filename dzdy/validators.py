import re

__author__ = 'TimeWz667'

"""
Validation for values.
Partially adapted from validators.py in WTForms
"""


class ValidationError(ValueError):
    def __init__(self, message='', *args, **kwargs):
        """
        Error message during validation
        Args:
            message:
        """
        ValueError.__init__(self, message, *args, **kwargs)


class Number:
    def __init__(self, lower=None, upper=None):
        self.Lower = lower
        self.Upper = upper

    def __call__(self, data):
        if data:
            if (self.Lower is not None and data < self.Lower) or (self.Upper is not None and data > self.Upper):
                raise ValidationError('Value does not fit the range')
        else:
            raise ValidationError('Value is not assigned')


class InSet:
    def __init__(self, values):
        self.Values = values

    def __call__(self, data):
        if data:
            if data not in self.Values:
                raise ValidationError('Value does not in the set')
        else:
            raise ValidationError('Value is not assigned')


class RegExp:
    def __init__(self, reg, flags=0):
        self.Reg = re.compile(reg, flags)

    def __call__(self, data):
        match = self.Reg.match(data or '')
        if not match:
            raise ValidationError('Value parsing failed')


class ListSize:
    def __init__(self, size):
        self.Size = size

    def __call__(self, data):
        try:
            if len(data) is not self.Size:
                raise ValidationError('Array does not fit the length')
        except AttributeError:
            raise ValidationError('Value is not an array')


class ProbTab:
    def __init__(self):
        pass

    def __call__(self, data):
        try:
            for v in data.values():
                if v < 0:
                    raise ValidationError('Table contains negative probability')
        except AttributeError:
            raise ValidationError('Value is not an probability table')


def check_all(values, vld):
    for k, v in values.items():
        try:
            vld[k](v)
        except ValidationError:
            return False
        except KeyError:
            return True
    return True


if __name__ == '__main__':
    vld0 = {
        'N1': Number(lower=0),
        'N2': Number(upper=100),
        'N3': Number(lower=0, upper=100),
        'S1': InSet(['A', 'B', 'C']),
        'R1': RegExp(r'\w+@\w+', re.I)
    }

    vs = {'N1': 10}
    print(check_all(vs, vld0))
    vs = {'N2': 101}
    print(check_all(vs, vld0))
    vs = {'N3': -1}
    print(check_all(vs, vld0))
    vs = {'S1': 'A'}
    print(check_all(vs, vld0))
    vs = {'S1': 'D'}
    print(check_all(vs, vld0))
    vs = {'R1': 'A@B'}
    print(check_all(vs, vld0))
    vs = {'R1': 'A!B'}
    print(check_all(vs, vld0))
