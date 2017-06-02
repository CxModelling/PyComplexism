from abc import ABCMeta, abstractmethod
import json


__author__ = 'TimeWz667'


class AbsDirector(metaclass=ABCMeta):
    def __init__(self):
        self.SC = None

    def set_simulation_core(self, sc):
        self.SC = sc

    @abstractmethod
    def clone(self, mod, pc):
        pass

    @abstractmethod
    def freeze(self, mod):
        pass

    @abstractmethod
    def defrost(self, js):
        pass

    def save_to_json(self, mod, file):
        js = self.freeze(mod)
        with open(file, 'w') as outfile:
            json.dump(js, outfile)

    def load_from_json(self, file):
        with open(file) as data_file:
            js = json.load(data_file)
        return self.defrost(js)
