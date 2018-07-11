from abc import ABCMeta, abstractmethod
import re
from collections import OrderedDict

__author__ = 'TimeWz667'
__all__ = ['EventListenerSet', 'ImpulseChecker', 'ImpulseResponse',
           'StartsWithChecker', 'RegexChecker']

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

    @property
    def AllChecker(self):
        return self.Listeners.keys()

    def apply_shock(self, disclosure, model_foreign, model_local, ti):
        shocked = False
        for k, v in self.Listeners.items():
            if k.needs(disclosure):
                v.apply_shock(disclosure, model_foreign, model_local, ti)
                shocked = True
        return shocked

    def is_jsonable(self):
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
        #todo
        pass


class ImpulseChecker(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, disclosure):
        pass

    @abstractmethod
    def to_json(self):
        pass

    @staticmethod
    @abstractmethod
    def from_json(js):
        pass


class ImpulseResponse(metaclass=ABCMeta):
    @abstractmethod
    def __ceil__(self, disclosure, model_foreign, model_local, ti):
        pass

    def to_json(self):
        pass

    @staticmethod
    @abstractmethod
    def from_json(js):
        pass


class StartsWithChecker(ImpulseChecker):
    def __init__(self, s):
        self.Start = s

    def __call__(self, disclosure):
        return disclosure.What.startsWith(self.Start)

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
        self.RegexF = re.compile(regex, flag)

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


class EventListener(metaclass=ABCMeta):
    @abstractmethod
    def needs(self, disclosure, model_local):
        pass

    @abstractmethod
    def apply_shock(self, disclosure, model_foreign, model_local, ti, arg=None):
        pass
