from abc import ABCMeta, abstractmethod

__all__ = ['ImpulseResponse', 'get_impulse_response',
           'ValueImpulse', 'AddOneImpulse', 'MinusOneImpulse', 'MinusNImpulse'
           ]


class ImpulseResponse(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, disclosure, model_foreign, model_local, ti):
        pass

    def to_json(self):
        raise {'Type': type(self)}

    @staticmethod
    def from_json(js):
        raise AttributeError('Unmatched form')


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
        return 'impulse', {'k': self.Target, 'v': disclosure[self.Value]}

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


class AddOneImpulse(ImpulseResponse):
    def __init__(self, target):
        """
        (Equation-based model only)
        Making add one to a targeted variable
        :param target: target variable
        """
        self.Target = target

    def __call__(self, disclosure, model_foreign, model_local, ti):
        return 'add', {'y': self.Target, 'n': 1}

    def to_json(self):
        js = ImpulseResponse.to_json(self)
        js['Target'] = self.Target
        return js

    @staticmethod
    def from_json(js):
        try:
            return AddOneImpulse(js['Target'])
        except KeyError:
            ImpulseResponse.from_json(js)


class MinusOneImpulse(ImpulseResponse):
    def __init__(self, target):
        """
        (Equation-based model only)
        Making minus one to a targeted variable
        :param target: target variable
        """
        self.Target = target

    def __call__(self, disclosure, model_foreign, model_local, ti):
        return 'del', {'y': self.Target, 'n': 1}

    def to_json(self):
        js = ImpulseResponse.to_json(self)
        js['Target'] = self.Target
        return js

    @staticmethod
    def from_json(js):
        try:
            return MinusOneImpulse(js['Target'])
        except KeyError:
            ImpulseResponse.from_json(js)


class MinusNImpulse(ImpulseResponse):
    def __init__(self, target, value):
        """
        (Equation-based model only)
        Making minus n to a targeted variable
        :param target: target variable
        :param value: index of amount
        """
        self.Target = target
        self.Value = value

    def __call__(self, disclosure, model_foreign, model_local, ti):
        return 'del', {'y': self.Target, 'n': disclosure[self.Value]}

    def to_json(self):
        js = ImpulseResponse.to_json(self)
        js['Target'] = self.Target
        return js

    @staticmethod
    def from_json(js):
        try:
            return MinusOneImpulse(js['Target'])
        except KeyError:
            ImpulseResponse.from_json(js)


ResponseLibrary = {
    'ValueImpulse': ValueImpulse,
    'AddOneImpulse': AddOneImpulse,
    'MinusOneImpulse': MinusOneImpulse,
    'MinusNImpulse': MinusNImpulse
}


def get_impulse_response(checker_type, **kwargs):
    try:
        ResponseLibrary[checker_type].from_json(kwargs)
    except KeyError:
        raise KeyError('Unknown type of response')
