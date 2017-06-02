import numpy.random as rd


__author__ = 'TimeWz667'


class FillUpSet:
    def __init__(self):
        self.FillUps = list()

    def append(self, f):
        if callable(f):
            self.FillUps.append(f)

    def __call__(self, info=None):
        info = info if info else {}
        for f in self.FillUps:
            info = f(info)
        return info


class FillBinary:
    def __init__(self, name, prob, tf=(1, 0)):
        self.Name = name
        self.Prob = prob
        self.TrueFalse = tf

    def __call__(self, info):
        if self.Name in info:
            return info
        info[self.Name] = \
            self.TrueFalse[0] if rd.random() < self.Prob else self.TrueFalse[1]
        return info


class FillNormal:
    def __init__(self, name, mu, std):
        self.Name = name
        self.Mu = mu
        self.Std = std

    def __call__(self, info):
        if self.Name in info:
            return info
        info[self.Name] = rd.normal(self.Mu, self.Std)
        return info


if __name__ == '__main__':
    fs_test = FillUpSet()
    fs_test.append(FillBinary('Sex', 0.5, ['M', 'F']))
    fs_test.append(FillNormal('Height', 170, 10))
    print(fs_test({}))
    print(fs_test({}))



