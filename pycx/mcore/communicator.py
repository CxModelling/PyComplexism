from collections import OrderedDict
from pycx.mcore.impresponse import get_impulse_response, ImpulseResponse
from pycx.mcore.impchecker import get_impulse_checker, ImpulseChecker

__author__ = 'TimeWz667'
__all__ = ['EventListenerSet']

# The job of EventListener
# 1. Check if an external event have impact
# 2. Extract information in the disclosure
# 3. Render responding nodes
# 4. Draw impact-response


class EventListenerSet:
    def __init__(self):
        self.Listeners = OrderedDict()

    def initialise(self, ti):
        for k, v in self.Listeners.items():
            try:
                k.initialise(ti)
            except AttributeError:
                pass

            try:
                v.initialise(ti)
            except AttributeError:
                pass

    def add_impulse_response(self, checker, event):
        self.Listeners[checker] = event

    def add_impulse_response_from_json(self, chk_j, res_j):
        try:
            chk = get_impulse_checker(chk_j['Type'], **chk_j)
            res = get_impulse_response(res_j['Type'], **res_j)
            self.add_impulse_response(chk, res)
        except KeyError as e:
            raise e

    @property
    def AllChecker(self):
        return self.Listeners.keys()

    def apply_shock(self, disclosure, model_foreign, model_local, ti):
        shocked = False
        for k, v in self.Listeners.items():
            if k(disclosure):
                try:
                    action, values = v(disclosure, model_foreign, model_local, ti)
                    model_local.shock(ti, action, **values)
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
