from abc import ABCMeta, abstractmethod
import re
from collections import OrderedDict

__author__ = 'TimeWz667'
__all__ = ['EventListenerSet', 'ImpulseChecker', 'ImpulseResponse',
           'StartsWithChecker', 'RegexChecker', 'InclusionChecker',
           'InitialChecker',
           'ValueImpulse']

# The job of EventListener
# 1. Check if an external event have impact
# 2. Extract information in the disclosure
# 3. Render responding nodes
# 4. Draw impact-response


class EventListenerSet:
    def __init__(self):
        self.Listeners = OrderedDict()

    def add_impulse_response(self, checker, event):
        self.Listeners[checker] = event

    def add_impulse_response_from_json(self, ck_j, re_j):
        # todo
        pass

    @property
    def AllChecker(self):
        return self.Listeners.keys()

    def apply_shock(self, disclosure, model_foreign, model_local, ti):
        shocked = False
        for k, v in self.Listeners.items():
            if k(disclosure):
                try:
                    action, values = v(disclosure, model_foreign, model_local, ti)
                    model_local.shock(ti, action, values)
                    shocked = True
                except TypeError:
                    pass
        return shocked

    def is_jsonifiable(self):
        for k, v in self.Listeners.items():
            if not isinstance(k, ImpulseChecker):
                return False
            if not isinstance(v, ImpulseResponse):
                return False
        return True

    def to_json(self):
        return [{'Impulse': k.to_json(), 'Response': v.to_json()} for k, v in self.Listeners.items()]

    @staticmethod
    def from_json(js):
        els = EventListenerSet()
        for d in js:
            els.add_impulse_response_from_json(d['Impulse'], d['Response'])
        return els


class ImpulseChecker(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, disclosure):
        pass

    def to_json(self):
        raise AttributeError('Not jsonifiable')

    @staticmethod
    def from_json(js):
        raise AttributeError('Not jsonifiable')


class ImpulseResponse(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, disclosure, model_foreign, model_local, ti):
        pass

    def to_json(self):
        raise {'Type': type(self)}

    @staticmethod
    def from_json(js):
        raise AttributeError('Unmatched form')


class StartsWithChecker(ImpulseChecker):
    def __init__(self, s):
        self.Start = s

    def __call__(self, disclosure):
        return disclosure.What.startswith(self.Start)

    def to_json(self):
        return {
            'Type': 'StartsWith',
            'Start': self.Start
        }

    @staticmethod
    def from_json(js):
        return StartsWithChecker(js['Start'])


class RegexChecker(ImpulseChecker):
    def __init__(self, regex, flag=0):
        self.Regex = regex
        self.Flag = flag
        self.RegexF = re.compile(regex, flags=flag)

    def __call__(self, disclosure):
        return bool(self.RegexF.match(disclosure.What))

    def to_json(self):
        return {
            'Type': 'Regex',
            'Regex': self.Regex,
            'Flag': self.Flag
        }

    @staticmethod
    def from_json(js):
        return RegexChecker(js['Regex'], js['Flag'])


class InclusionChecker(ImpulseChecker):
    def __init__(self, included):
        self.Inclusion = list(included)

    def __call__(self, disclosure):
        return disclosure.What in self.Inclusion

    def to_json(self):
        return {
            'Type': 'Inclusion',
            'Inclusion': self.Inclusion
        }

    @staticmethod
    def from_json(js):
        return InclusionChecker(js['Inclusion'])


class InitialChecker(StartsWithChecker):
    def __init__(self):
        StartsWithChecker.__init__(self, 'initialise')


class ValueImpulse(ImpulseResponse):
    def __init__(self, target, value):
        """
        Making an impulse on target considering a value of the disclosed
        :param target: target variable
        :param value: index referred to a value of disclosure
        """
        self.Target = target
        self.Value = value

    def __call__(self, disclosure, model_foreign, model_local, ti):
        return 'Impulse', {'k': self.Target, 'v': disclosure[self.Value]}

    def to_json(self):
        js = ImpulseResponse.to_json(self)
        js['Target'] = self.Target
        js['Value'] = self.Value
        return js

    @staticmethod
    def from_json(js):
        try:
            return ValueImpulse(js['Target'], js['Value'])
        except KeyError:
            ImpulseResponse.from_json(js)
