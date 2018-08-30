from abc import ABCMeta, abstractmethod
import re

__all__ = ['ImpulseChecker', 'get_impulse_checker',
           'StartsWithChecker', 'RegexChecker',
           'InclusionChecker', 'InitialChecker', 'IsChecker', 'WhoStartWithChecker']


class ImpulseChecker(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, disclosure):
        pass

    def initialise(self, ti):
        pass

    def to_json(self):
        return {
            'Type': type(self)
        }

    @staticmethod
    def from_json(js):
        raise AttributeError('Unmatched type')

    def clone(self):
        js = self.to_json()
        return self.__class__.from_json(js)


class StartsWithChecker(ImpulseChecker):
    def __init__(self, s):
        self.Start = s

    def __call__(self, disclosure):
        return disclosure.What.startswith(self.Start)

    def to_json(self):
        js = ImpulseChecker.to_json(self)
        js['Start'] = self.Start
        return js

    @staticmethod
    def from_json(js):
        try:
            return StartsWithChecker(js['Start'])
        except KeyError:
            ImpulseChecker.from_json(js)


class IsChecker(ImpulseChecker):
    def __init__(self, s):
        self.Message = s

    def __call__(self, disclosure):
        return disclosure.What == self.Message

    def to_json(self):
        js = ImpulseChecker.to_json(self)
        js['Message'] = self.Message
        return js

    @staticmethod
    def from_json(js):
        try:
            return IsChecker(js['Message'])
        except KeyError:
            ImpulseChecker.from_json(js)


class RegexChecker(ImpulseChecker):
    def __init__(self, regex, flag=0):
        self.Regex = regex
        self.Flag = flag
        self.RegexF = re.compile(regex, flags=flag)

    def __call__(self, disclosure):
        return bool(self.RegexF.match(disclosure.What))

    def to_json(self):
        js = ImpulseChecker.to_json(self)
        js['Regex'] = self.Regex
        js['Flag'] = self.Flag
        return js

    @staticmethod
    def from_json(js):
        try:
            return RegexChecker(js['Regex'], js['Flag'])
        except KeyError:
            ImpulseChecker.from_json(js)


class InclusionChecker(ImpulseChecker):
    def __init__(self, included):
        self.Inclusion = list(included)

    def __call__(self, disclosure):
        return disclosure.What in self.Inclusion

    def to_json(self):
        js = ImpulseChecker.to_json(self)
        js['Inclusion'] = self.Inclusion
        return js

    @staticmethod
    def from_json(js):
        try:
            return InclusionChecker(js['Inclusion'])
        except KeyError:
            ImpulseChecker.from_json(js)


class InitialChecker(IsChecker):
    def __init__(self):
        IsChecker.__init__(self, 'initialise')


class WhoStartWithChecker(ImpulseChecker):
    def __init__(self, who, something):
        self.Who = who
        self.Start = something

    def __call__(self, disclosure):
        return disclosure.What.startswith(self.Start) and disclosure.Who == self.Who

    def to_json(self):
        js = ImpulseChecker.to_json(self)
        js['Start'] = self.Start
        js['Who'] = self.Who
        return js

    @staticmethod
    def from_json(js):
        try:
            return WhoStartWithChecker(js['Who'], js['Start'])
        except KeyError:
            ImpulseChecker.from_json(js)


CheckerLibrary = {
    'InitialChecker': ImpulseChecker,
    'IsChecker': IsChecker,
    'StartsWithChecker': StartsWithChecker,
    'RegexChecker': RegexChecker,
    'InclusionChecker': InclusionChecker,
    'WhoStartWithChecker': WhoStartWithChecker
}


def get_impulse_checker(checker_type, **kwargs):
    try:
        CheckerLibrary[checker_type].from_json(kwargs)
    except KeyError:
        raise KeyError('Unknown type of checker')
