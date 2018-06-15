from complexism.mcore.modelnode import BranchModel, LeafModel
from complexism.mcore.simulator import Simulator
from complexism.element import Event
import numpy.random as rd


class Country(BranchModel):
    def __init__(self, name):
        BranchModel.__init__(self, name)
        self.Models = dict()
        self.Check = False

    def all_models(self) -> dict:
        return self.Models

    def get_model(self, k):
        return self.Models[k]

    def do_request(self, request):
        self.Check = True
        self.disclose(request.Message, request.When)

    def find_next(self):
        if not self.Check:
            self.request(Event('Country', 5), 'self')

    def trigger_external_impulses(self, disclosure, model, time):
        # print(self.Name, disclosure, time)
        pass


class City(BranchModel):
    def __init__(self, name):
        BranchModel.__init__(self, name)
        self.Models = dict()
        self.Check = False

    def all_models(self) -> dict:
        return self.Models

    def get_model(self, k):
        return self.Models[k]

    def do_request(self, request):
        self.Check = True
        self.disclose(request.Message, request.When)

    def find_next(self):
        if not self.Check:
            self.request(Event('broadcast', 3), 'self')

    def trigger_external_impulses(self, disclosure, model, ti):
        # print(self.Name, disclosure, time)
        pass


class School(LeafModel):
    def __init__(self, name):
        LeafModel.__init__(self, name, None)
        self.Last = 0

    def reset(self, ti):
        self.Last = ti

    def find_next(self):
        self.request(Event(self.Name, self.Last+rd.random()*5), 'student')

    def do_request(self, request):
        self.disclose("teach", self.Name)
        self.Last = request.When

    def trigger_external_impulses(self, disclosure, model, time):
        # print(self.Name, disclosure, time)
        pass


if __name__ == '__main__':

    tw = Country('Taiwan')
    tp = City('Taipei')
    tw.Models['Taipei'] = tp

    tn = City('Tainan')
    tw.Models['Tainan'] = tn

    for st in range(2):
        n = 'S{}'.format(st)
        tp.Models[n] = School(n)

    for st in range(2):
        n = 'S{}'.format(st)
        tn.Models[n] = School(n)

    s = Simulator(tw)
    s.simulate(None, 0, 10, 1)
