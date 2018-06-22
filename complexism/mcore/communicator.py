from abc import ABCMeta, abstractmethod
import re

__author__ = 'TimeWz667'


# The job of EventListener
# 1. Check if an external event have impact
# 2. Extract information in the disclosure
# 3. Render responding nodes
# 4. Draw impact-response

class EventListener(metaclass=ABCMeta):
    @abstractmethod
    def needs(self, disclosure, model_local):
        pass

    @abstractmethod
    def apply_shock(self, disclosure, model_foreign, model_local, ti, arg=None):
        pass


class RegexEventListener(EventListener):
    def __init__(self, regex, fn, flag=re.I):
        self.Pattern = re.compile(regex, flag)
        self.Function = fn

    def needs(self, disclosure, local_model):

        return self.Pattern.match(disclosure.What)

    @abstractmethod
    def apply_shock(self, disclosure, model_foreign, model_local, ti, arg=None):
        pass
