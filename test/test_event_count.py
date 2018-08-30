import unittest
from complexism.misc.counter import *


class Model:
    def __init__(self, name):
        self.Name = name

    @count('A')
    def do_a(self):
        pass

    @count('B')
    def do_b(self):
        pass

    @count()
    def do_c(self):
        pass


class EventRecordTestCase(unittest.TestCase):
    def setUp(self):
        self.M = Model('Test')

    def test_counting(self):
        start_counting()
        for _ in range(100):
            self.M.do_a()

        for _ in range(200):
            self.M.do_b()

        self.M.do_c()
        stop_counting()
        dat = get_counting_results()
        self.assertEqual(dat['Test:A'][0], 100)
        self.assertEqual(dat['Test:B'][0], 200)
        self.assertEqual(dat['Test:Event'][0], 1)


if __name__ == '__main__':
    unittest.main()
