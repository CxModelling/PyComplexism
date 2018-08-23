from abc import ABCMeta, abstractmethod
from collections import Counter
from . import Request, Disclosure
__author__ = 'TimeWz667'

DefaultScheduler = "PriorityQueue"


class AbsScheduler(metaclass=ABCMeta):
    def __init__(self, location):
        self.Location = location
        self.OwnTime = float('inf')
        self.GloTime = float('inf')
        self.Upcoming = set()
        self.AtomRequests = dict()
        self.Requests = list()
        self.Disclosures = list()
        self.NumAtoms = 0
        self.Counter = Counter()

    def add_atom(self, atom):
        self.join_scheduler(atom)
        atom.set_scheduler(self)
        self.NumAtoms += 1

    def remove_atom(self, atom):
        atom.drop_next()
        atom.detach_scheduler()
        self.leave_scheduler(atom)
        self.pop_from_upcoming(atom)
        self.NumAtoms -= 1

    @abstractmethod
    def join_scheduler(self, atom):
        pass

    @abstractmethod
    def leave_scheduler(self, atom):
        pass

    @abstractmethod
    def pop_from_upcoming(self, atom):
        self.Upcoming.remove(atom)
        if not self.Upcoming:
            self.OwnTime = float('inf')

    @abstractmethod
    def await(self, atom):
        pass

    def add_scheduler_atom(self, atom):
        self.add_atom(atom)
        self.await(atom)

    @abstractmethod
    def reschedule_all(self):
        pass

    @abstractmethod
    def reschedule_waiting(self):
        pass

    @abstractmethod
    def find_upcoming_atoms(self):
        pass

    def extract_current_request(self):
        for atom in self.Upcoming:
            event = atom.Next
            self.AtomRequests[atom] = Request(event, atom.Name, self.Location)

    def check_current_requests(self):
        if self.NumAtoms <= 0:
            return

        if not self.Upcoming or not (self.Upcoming > self.AtomRequests.keys()):
            self.find_upcoming_atoms()
            self.AtomRequests = dict()

        if not self.AtomRequests:
            self.extract_current_request()

    def find_next(self):
        self.reschedule_waiting()
        self.check_current_requests()
        self.Requests = list(self.AtomRequests.values())
        self.GloTime = min(self.OwnTime, self.GloTime)

    def is_executable(self):
        return self.GloTime is self.OwnTime

    def up_scale_requests(self, loc):
        return [req.up_scale(loc) for req in self.Requests]

    def append_lower_schedule(self, lower):
        if not lower.Requests:
            return

        ti = lower.Time
        if ti < self.Time:
            self.Requests = lower.up_scale_requests(self.Location)
            self.Time = ti
        elif ti == self.Time:
            if self.Requests:
                self.Requests += lower.up_scale_requests(self.Location)
        else:
            return

    def append_request_from_source(self, event, who):
        # todo validate
        if event.Time < self.Time:
            self.Requests = [Request(event, who, self.Location)]
            self.Time = event.Time
        elif event.Time == self.Time:
            self.Requests.append(Request(event, who, self.Location))
        else:
            return

    def append_disclosure(self, dss: Disclosure):
        """
        Append a disclosure
        :param dss: message to be exposed
        """
        self.Disclosures.append(dss)

    def append_disclosure_from_source(self, msg, who, **kwargs):
        dss = Disclosure(msg, who, self.Location, **kwargs)
        self.append_disclosure(dss)


    def fetch_requests(self, rs):
        rs_out = [req for req in self.Requests if req not in rs]
        for req in rs_out:
            req.Event.cancel()

        self.Requests = rs

    def pop_lower_requests(self):
        gp = groupby(self.Requests, lambda x: x.reached())
        lower, current = list(), list()
        for k, g in gp:
            if k:
                current += list(g)
            else:
                lower += [req.down_scale() for req in g]

        if lower:
            pop = {k: [req for _, req in g] for k, g in groupby(lower, lambda x: x[1].Group)}
        else:
            pop = dict()

        self.Requests = current

        return pop



