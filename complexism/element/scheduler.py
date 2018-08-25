from abc import ABCMeta, abstractmethod
from collections import Counter
from . import Request, Disclosure
__author__ = 'TimeWz667'
__all__ = ['get_scheduler', '']

DefaultScheduler = "PriorityQueue"


def get_scheduler(loc, tp=None):
    tp = tp if tp else DefaultScheduler
    if tp == "PriorityQueue":
        return None
    elif tp == "Looping":
        return None


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

    def __len__(self):
        return len(self.Requests) + len(self.Disclosures)

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

        ti = lower.GloTime
        if ti < self.GloTime:
            self.Requests = lower.up_scale_requests(self.Location)
            self.GloTime = ti
        elif ti == self.GloTime:
            self.Requests += lower.up_scale_requests(self.Location)
        else:
            return

    def fetch_requests(self, rs):
        # rs_out = [req for req in self.Requests if req not in rs]
        # for req in rs_out:
        #     req.Event.cancel()
        self.Requests = list(rs)
        self.Counter['Requests'] += len(rs)

    def append_request_from_source(self, event, who):
        # todo validate
        if event.Time < self.GloTime:
            self.Requests = [Request(event, who, self.Location)]
            self.GloTime = event.Time
        elif event.Time == self.GloTime:
            self.Requests.append(Request(event, who, self.Location))
        else:
            return

    def pop_lower_requests(self):
        current = list()
        lower = dict()

        for req in self.Requests:
            if req.reached():
                continue
            try:
                _, req = req.down_scale()
                lower[req.Group].append(req)
            except KeyError:
                lower[req.Group] = [req]

        self.Requests = current

        return lower

    def append_disclosure(self, dss: Disclosure):
        """
        Append a disclosure
        :param dss: message to be exposed
        """
        self.Disclosures.append(dss)

    def append_disclosure_from_source(self, msg, who, **kwargs):
        dss = Disclosure(msg, who, self.Location, **kwargs)
        self.append_disclosure(dss)

    def pop_disclosures(self):
        ds, self.Disclosures = self.Disclosures, list()
        self.Counter['Disclosure'] + len(ds)
        return ds

    def execution_completed(self):
        self.Requests.clear()
        self.AtomRequests = dict()
        self.Upcoming.clear()
        self.OwnTime = float('inf')

    def cycle_completed(self):
        """
        To finish a cycle without erase un-executed requests
        """
        self.Requests.clear()
        self.Disclosures.clear()
        self.GloTime = self.OwnTime

    def __repr__(self):
        return 'Scheduler{Location={}, #Atoms={}, #Requests={}, #Disclosure={}, Time={}'.format(
            self.Location, self.NumAtoms, len(self.Requests), len(self.Disclosures), self.OwnTime
        )


class LoopingScheduler(AbsScheduler):
    def __init__(self, location):
        AbsScheduler.__init__(self, location)
        self.Atoms = list()
        self.Waiting = set()

    def join_scheduler(self, atom):
        self.Atoms.append(atom)
        self.Waiting.add(atom)

    def leave_scheduler(self, atom):
        self.Atoms.remove(atom)
        self.Waiting.remove(atom)

    def await(self, atom):
        self.Waiting.add(atom)
        self.pop_from_upcoming(atom)

    def reschedule_all(self):
        self.Upcoming.clear()
        self.OwnTime = float('inf')
        self.reschedule_set(self.Atoms)
        self.Waiting.clear()

    def reschedule_waiting(self):
        if self.Upcoming:
            self.reschedule_set(self.Waiting)
            self.Waiting.clear()
        else:
            self.reschedule_all()

    def find_upcoming_atoms(self):
        if not self.Upcoming:
            self.reschedule_all()

    def reschedule_set(self, atoms):
        for atom in atoms:
            event = atom.Next
            if event.Time < self.OwnTime:
                self.Upcoming.clear()
                self.Upcoming.add(atom)
                self.OwnTime = event.Time
            elif event.Time == self.OwnTime:
                self.Upcoming.add(atom)

        self.Counter['Requeuing'] += len(atoms)


class PriorityQueueScheduler(AbsScheduler):
    CAP = 10
    def __init__(self, location):
        AbsScheduler.__init__(self, location)


    def leave_scheduler(self, atom):
        pass

    def await(self, atom):
        pass

    def reschedule_all(self):
        pass

    def reschedule_waiting(self):
        pass

    def find_upcoming_atoms(self):
        pass

    def join_scheduler(self, atom):
        pass