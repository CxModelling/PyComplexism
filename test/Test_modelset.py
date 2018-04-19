import unittest
from complexism import *


class ConstantObs(Observer):
    def update_dynamic_Observations(self, model, flow, ti):
        flow[model.Name+"F"] = ti

    def read_statics(self, model, tab, ti):
        tab[model.Name] = model.Last


class ConstantModel(LeafModel):
    def __init__(self, name, dt):
        LeafModel.__init__(self, name, ConstantObs())
        self.Timer = Clock(dt=dt)
        self.Last = 0

    def reset(self, ti):
        self.Timer.initialise(ti, ti)

    def do_request(self, req):
        self.Timer.update(req.Time)
        self.Last = req.Time
        print(req)

    def find_next(self):
        ti = self.Timer.get_next()
        evt = Event(self.Name, ti)
        self.Requests.append_src("Step", evt, ti)

    def clone(self, **kwargs):
        pass


class MyTestCase(unittest.TestCase):
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)
        self.Mod1 = ConstantModel("A", 0.4)
        self.Mod2 = ConstantModel("B", 0.7)
        self.MM = ModelSet("AB")
        self.MM.append(self.Mod1)
        self.MM.append(self.Mod2)
        self.MM.link("A@A", "AB@C")
        self.MM.add_obs_model("A")
        self.MM.add_obs_model("B")
        self.MM.add_obs_model("*")

    def test_const_model(self):
        simulate(self.Mod1, None, 0, 3)
        self.Mod1.Obs.print()

    def test_multi_model(self):
        simulate(self.MM, {"A": None, "B": None}, 0, 3)
        self.MM.Obs.print()
        self.MM.Models['A'].Obs.print()
        self.MM.Models['B'].Obs.print()


if __name__ == '__main__':
    unittest.main()
