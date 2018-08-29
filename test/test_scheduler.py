import unittest
import complexism as cx
from complexism.element import Event
from complexism.agentbased import SingleIndividualABM, Population
import complexism.multimodel as mm


class Stepper(cx.GenericAgent):
    def __init__(self, name, step_size=1):
        cx.GenericAgent.__init__(self, name)
        self.Last = 0
        self.StepSize = step_size

    def update_time(self, ti):
        self.Last += 0.5

    def find_next(self):
        return Event('Step', self.StepSize+self.Last)

    def execute_event(self):
        self.Last = self.Next.Time

    def initialise(self, ti, model, *args, **kwargs):
        self.Last = ti

    def reset(self, ti, model, *args, **kwargs):
        self.Last = ti


class GenericAgentTestCase(unittest.TestCase):
    def setUp(self):
        ag = Stepper('A1', step_size=1)
        self.Model = SingleIndividualABM('Test', ag)

    def test_simulate(self):
        self.Model.initialise(0, None)
        self.Model.collect_requests()
        while self.Model.Scheduler.GloTime < 10:
            self.Model.collect_requests()
            requests = self.Model.collect_requests()
            self.print(requests)
            self.Model.fetch_requests(requests)
            self.Model.execute_requests()
            self.Model.exit_cycle()
            self.Model.collect_requests()
            print()

    def print(self, requests):
        print('Time', self.Model.Scheduler.GloTime)
        for req in requests:
            print('\t',req)


if __name__ == '__main__':
    unittest.main()
