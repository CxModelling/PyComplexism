from abc import ABCMeta, abstractmethod


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


ResponseLibrary = {
    'ValueImpulse': ValueImpulse
}


def get_impulse_response(checker_type, **kwargs):
    try:
        ResponseLibrary[checker_type].from_json(kwargs)
    except KeyError:
        raise KeyError('Unknown type of response')
