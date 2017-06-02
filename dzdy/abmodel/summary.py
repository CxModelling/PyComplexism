import pandas as pd

__author__ = 'TimeWz667'


def demography_summary(obs, model, ti):
    dat = model.Pop.get_info_table()

    for k, v in dat.groupby('Sex').mean().iterrows():
        obs['AvgAge{}'.format(k[0])] = float(v)

    obs['Num'] = dat.shape[0]
    for k, v in dat.groupby('Sex').count().iterrows():
        obs['Num.{}'.format(k[0])] = float(v)

    y, o = sum(dat.Age <= 15), sum(dat.Age >= 65)
    obs['Num.Young'] = y
    obs['Num.Mid'] = len(dat) - y - o
    obs['Num.Old'] = o
    return obs


def make_average(col):
    def f(obs, model, ti):
        dat = [ag.Info[col] for ag in model.agents]
        obs['E[{}]'.format(col)] = sum(dat)/len(dat)
        return obs
    return f


def make_std(col):
    def f(obs, model, ti):
        dat = [ag.Info[col] for ag in model.agents]
        dat = pd.Series(dat)
        dat.std()
        obs['Std[{}]'.format(col)] = float(dat.std())
        return obs
    return f