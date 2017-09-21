import pandas as pd
__author__ = 'TimeWz667'


class Observer:
    def __init__(self):
        self.Last = None
        self.TimeSeries = list()

    def __getitem__(self, item):
        try:
            return self.Last[item]
        except KeyError:
            return 0

    def renew(self):
        self.TimeSeries = list()

    def point_observe(self, model, ti):
        pass

    def after_shock_observe(self, model, ti):
        pass

    def push_observation(self):
        self.TimeSeries.append(self.Last)

    def observe(self, model, ti):
        self.single_observe(model, ti)
        self.push_observation()

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
