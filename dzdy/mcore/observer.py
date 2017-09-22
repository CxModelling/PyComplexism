import pandas as pd
from collections import OrderedDict
__author__ = 'TimeWz667'


class Observer:
    def __init__(self):
        self.Last = OrderedDict()
        self.Current = self.Last
        self.TimeSeries = list()

    def __getitem__(self, item):
        try:
            return self.Current[item]
        except KeyError:
            return 0

    def renew(self):
        self.TimeSeries = list()
        self.Last = OrderedDict()
        self.Current = self.Last

    def observe_fully(self, model, ti):
        self.initialise_observation(model, ti)
        self.update_observation(model, ti)
        self.push_observation(ti)

    def initialise_observation(self, model, ti):
        pass

    def update_observation(self, model, ti):
        pass

    def push_observation(self, ti):
        self.Current['Time'] = ti
        self.TimeSeries.append(self.Current)
        self.Last, self.Current = self.Current, OrderedDict()

        #else:
        #    self.TimeSeries[-1].update(self.Last)
        #    self.TimeSeries.append(self.Last)

    @property
    def observation(self):
        dat = pd.DataFrame(self.TimeSeries)
        return pd.DataFrame(self.TimeSeries, index=dat.Time)[[col for col in dat.columns if col is not 'Time']]

    def output_csv(self, file):
        self.observation.to_csv(file)

    def output_json(self, file):
        dat = pd.DataFrame(self.TimeSeries)
        dat.transpose().to_json(file)

    def print(self):
        print(self.observation)
