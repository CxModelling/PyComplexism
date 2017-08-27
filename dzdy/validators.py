import re
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import OrderedDict

__author__ = 'TimeWz667'

"""
Validation for values.
Partially adapted from validators.py in WTForms
"""

__all__ = ['Number', 'InSet', 'RegExp', 'ListSize', 'Options']


class ValidationError(ValueError):
    def __init__(self, message='', *args, **kwargs):
        """
        Error message during validation
        Args:
            message:
        """
        ValueError.__init__(self, message, *args, **kwargs)


class Validator(metaclass=ABCMeta):
    @abstractmethod
    def validate(self, value):
        pass

    @abstractmethod
    def filter(self, value):
        pass

    @abstractmethod
    def to_form(self):
        pass

    @abstractproperty
    def Default(self):
        pass


class Number(Validator):
    def __init__(self, lower=-float('inf'), upper=float('inf'), is_float=True, default=None):
        self.Lower = lower
        self.Upper = upper
        self.Float = is_float
        self.__default = default if default else min(max(0, self.Lower), self.Upper)

    def validate(self, value):
        if value:
            if self.Lower > value:
                raise ValidationError('Value is below lower bond')
            elif self.Upper < value:
                raise ValidationError('Value is beyond upper bond')
        else:
            raise ValidationError('Value is not assigned')

    def filter(self, data):
        data = min(data, self.Upper)
        data = max(data, self.Lower)
        try:
            data = float(data) if self.Float else int(data)
        except ValueError:
            data = self.Default
        return data

    def to_form(self):
        return {'Type': 'float' if self.Float else 'int',
                'Lower': self.Lower,
                'Upper': self.Upper,
                'Default': self.Default}

    @property
    def Default(self):
        return self.__default


class InSet(Validator):
    def __init__(self, values):
        self.Values = values

    @property
    def Default(self):
        return self.Values[0]

    def validate(self, value):
        if value:
            if value not in self.Values:
                raise ValidationError('Value does not in the set')
        else:
            raise ValidationError('Value is not assigned')

    def filter(self, data):
        if data in self.Values:
            return data
        else:
            return self.Default

    def to_form(self):
        return {'Type': 'items', 'Options': list(self.Values)}


class RegExp(Validator):
    def __init__(self, reg, flags=re.I, default=''):
        self.Reg = re.compile(reg, flags)
        self.__Default = default

    @property
    def Default(self):
        return self.__Default

    def validate(self, value):
        match = self.Reg.match(value or '')
        if not match:
            raise ValidationError('Value parsing failed')

    def filter(self, value):
        try:
            self.validate(value)
            return value
        except ValidationError:
            return self.Default

    def to_form(self):
        return {'Type': 'string', 'Default': self.__Default}


class ListSize(Validator):
    def __init__(self, size):
        self.Size = size

    def to_form(self):
        return {'Type': 'list'}

    def validate(self, value):
        try:
            if len(value) is not self.Size:
                raise ValidationError('Array does not fit the length')
        except AttributeError:
            raise ValidationError('Value is not an array')

    @property
    def Default(self):
        return None

    def filter(self, value):
        try:
            self.validate(value)
            return value
        except ValidationError:
            return None


class ProbTab(Validator):
    def __init__(self, default=None):
        try:
            self.validate(default)
            self.__Default = default
        except ValidationError:
            self.__Default = {'A': 0.5, 'B': 0.5}

    def __call__(self, data):
        try:
            for v in data.values():
                if v < 0:
                    raise ValidationError('Table contains negative probability')
        except AttributeError:
            raise ValidationError('Value is not an probability table')

    def to_form(self):
        return {'Type': 'table', 'Default': self.Default}

    def validate(self, value):
        try:
            for v in value.values():
                if v < 0:
                    raise ValidationError('Table contains negative probability')
        except AttributeError:
            raise ValidationError('Value is not an probability table')

    @property
    def Default(self):
        return self.__Default

    def filter(self, value):
        try:
            self.validate(value)
            return value
        except ValidationError:
            return self.Default


class Options:
    def __init__(self):
        self.Validators = OrderedDict()

    def __setitem__(self, key, value):
        self.Validators[key] = value

    def __getitem__(self, item):
        return self.Validators[item]

    def append(self, name, vld):
        self.Validators[name] = vld

    def check_all(self, values, log=None):
        for k, v in self.Validators.items():
            try:
                v.validate(values[k])
            except ValidationError as e:
                if log:
                    log.debug(e)
                return False
            except KeyError:
                if log:
                    log.debug('Argument {} not found'.format(k))
                return False
        return True

    def check_if_present(self, values, log=None):
        for k, v in self.Validators.items():
            try:
                v.validate(values[k])
            except ValidationError as e:
                if log:
                    log.debug(e)
                return False
            except KeyError:
                continue
        return True

    def get_form(self):
        fo = OrderedDict()
        for k, v in self.Validators.items():
            fo[k] = v.to_form()
        return fo

    def get_defaults(self):
        return {k: v.Default for k, v in self.Validators.items()}

    def modify(self, values, log=None):
        for k, v in self.Validators.items():
            try:
                val = values[k]
                val = v.filter(val)
            except KeyError:
                val = v.Default

            if val is not None:
                values[k] = val
            else:
                if log:
                    log.debug('Illegal argument: {}'.format(k))
                return False
        return True

    def extract(self, values, log=None):
        ex = dict()
        for k in self.Validators.keys():
            try:
                ex[k] = values[k]
            except KeyError:
                if log:
                    log.debug('Lost variable: {}'.format(k))
                return None
        return ex


if __name__ == '__main__':
    opts0 = Options()
    opts0.append('N1', Number(lower=0))
    opts0.append('N2', Number(upper=100))
    opts0.append('N3', Number(lower=0, upper=100, is_float=False))
    opts0.append('S1', InSet(['A', 'B', 'C']))
    opts0.append('R1', RegExp(r'\w+@\w+', re.I, 'A@B'))

    for f in opts0.get_form().items():
        print(f)

    test1 = {
        'N1': 0,
        'N2': -1,
        'N3': 0.5,
        'S1': 'G',
        'R1': 'A@?',
    }
    print(opts0.modify(test1))
    print(test1)

    test2 = {
        'N1': -1,
        'N3': 0.5,
        'S1': 'A',
        'R1': 'A@B',
    }
    print(opts0.modify(test2))
    print(test2)

    test3 = {
        'N1': 1,
        'N2': 1,
        'N3': 1,
        'N4': 0,
        'S1': 'A',
        'R1': 'A@B'
    }
    print(opts0.extract(test3))
