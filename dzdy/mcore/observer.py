import pandas as pd
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
__author__ = 'TimeWz667'


class Observer(metaclass=ABCMeta):
    def __init__(self, ext=True):
        self.Last = OrderedDict()
        self.Flow = OrderedDict()
        self.Mid = OrderedDict()
        self.TimeSeries = list()
        self.TimeSeriesMid = list()
        self.__ObsDt = 1
        self.ExtMid = ext

    @property
    def ObservationalInterval(self):
        return self.__ObsDt

    @ObservationalInterval.setter
    def ObservationalInterval(self, dt):
        if dt > 0:
            self.__ObsDt = dt

    def __getitem__(self, item):
        try:
            return self.Last[item]
        except KeyError:
            return 0

    def renew(self):
        self.TimeSeries = list()
        self.TimeSeriesMid = list()

    def __new_session(self, ti):
        self.Last = OrderedDict()
        self.Last['Time'] = ti + self.ObservationalInterval
        self.Flow.clear()
        if self.ExtMid:
            self.Mid = OrderedDict()
            self.Mid['Time'] = ti + self.ObservationalInterval

    @abstractmethod
    def read_statics(self, model, tab, ti):
        """

        :param model: model to be observed
        :param tab: table to store static information
        :param ti: observation time
        """
        pass

    @abstractmethod
    def update_dynamic_Observations(self, model, flow, ti):
        """

        :param model: model to be observed
        :param flow: table to store dynamic information
        :param ti: observation time
        """
        pass

    def initialise_observations(self, model, ti):
        self.renew()
        self.Last = OrderedDict()
        self.Last['Time'] = ti
        self.read_statics(model, self.Last, ti)

    def observe_routinely(self, model, ti):
        self.read_statics(model, self.Last, ti)
        self.update_dynamic_Observations(model, self.Flow, ti)

    def update_at_mid_term(self, model, ti):
        if self.ExtMid:
            self.read_statics(model, self.Mid, ti)

    def push_observations(self, ti):
        self.Last.update(self.Flow)
        self.TimeSeries.append(self.Last)
        if self.ExtMid:
            self.Mid.update(self.Flow)
            self.TimeSeriesMid.append(self.Mid)
        self.__new_session(ti)
        self.Flow.clear()

    def get_entry(self, i):
        try:
            return self.TimeSeries[i]
        except KeyError:
            return None

    def get_entry_at(self, ti):
        for ent in self.TimeSeries:
            if ent['Time'] == ti:
                return ent
        return None

    @property
    def Observations(self):
        dat = pd.DataFrame(self.TimeSeries)
        dat = dat.set_index('Time')
        return dat

    @property
    def AdjustedObservations(self):
        if not (self.ExtMid or len(self.TimeSeriesMid) is len(self.TimeSeries)):
            self.TimeSeriesMid = list()
            for f, t in zip(self.TimeSeries[:-1], self.TimeSeries[1:]):
                ent = OrderedDict()
                for k in f.keys():
                    ent[k] = (f[k] + t[k])/2
                self.TimeSeriesMid.append(ent)

        dat = pd.DataFrame(self.TimeSeriesMid)
        dat = dat.set_index('Time')
        return dat

    def output_csv(self, file, mid=False):
        if mid:
            self.AdjustedObservations.to_csv(file)
        else:
            self.Observations.to_csv(file)

    def output_json(self, file, mid=False):
        if mid:
            self.AdjustedObservations.to_json(file, orient='records')
        else:
            self.Observations.to_json(file, orient='records')

    def print(self, mid=False):
        if mid:
            print(self.AdjustedObservations)
        else:
            print(self.Observations)
