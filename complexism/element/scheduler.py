from abc import ABCMeta, abstractmethod
from collections import Counter
import heapq
from .event import Event
__author__ = 'TimeWz667'
__all__ = ['get_scheduler', 'DefaultScheduler', 'Request', 'Disclosure']

DefaultScheduler = 'PriorityQueue'
# DefaultScheduler = 'Looping'


class Disclosure:
    def __init__(self, what, who, where, **kwargs):
        self.What = what
        self.Who = who
        self.Where = [where] if isinstance(where, str) else where
        self.Arguments = dict(kwargs)

    def __getitem__(self, item):
        return self.Arguments[item]

    def up_scale(self, adr):
        """
        Append upper address into address
        :param adr: upper position
        :return: extended disclosure
        """
        new_adr = self.Where + [adr]
        return Disclosure(self.What, self.Who, new_adr, **self.Arguments)

    def sibling_scale(self):
        """
        Append a sibling indicator into address
        :return: extended disclosure
        """
        new_adr = self.Where + ['^']
        return Disclosure(self.What, self.Who, new_adr, **self.Arguments)

    def down_scale(self):
        """
        Decrease scale of the request
        :return: upper address and reformed request
        :rtype: tuple
        """
        new_adr = self.Where[:-1]
        return self.Where[-1], Disclosure(self.What, self.Who, new_adr, **self.Arguments)

    @property
    def Distance(self):
        return len(self.Where)

    def is_sibling(self):
        return self.Where[-1] == '^' and len(self.Where) is 2

    @property
    def Address(self):
        return '@'.join(self.Where)

    @property
    def Group(self):
        return self.Where[-1]

    @property
    def Source(self):
        return self.Where[0]

    def __repr__(self):
        if self.Arguments:
            args = ', '.join(self.Arguments.keys())
            return 'Disclosure({} did {} in {} with)'.format(
                self.Who, self.What, self.Address, args)
        else:
            return 'Disclosure({} did {} in {})'.format(self.Who, self.What, self.Address)

    def __str__(self):
        res = 'Disclose:\t{} did {} in {}'.format(self.Who, self.What, self.Address)
        if self.Arguments:
            args = ', '.join(self.Arguments.keys())
            res = '{} with {}'.format(res, args)
        return res


class Request:
    NullRequest = None

    def __init__(self, evt: Event, who, where):
        self.Who = who
        self.Where = [where] if isinstance(where, str) else where
        self.Event = evt

    @property
    def Message(self):
        return self.Event.Message

    @property
    def When(self):
        return self.Event.Time

    @property
    def What(self):
        return self.Event.Todo

    @property
    def Address(self):
        return '@'.join(self.Where)

    @property
    def Group(self):
        return self.Where[-1]

    def to_disclosure(self):
        return Disclosure(self.Message, self.Who, self.Where)

    def __repr__(self):
        return 'Request({} want to do {} in {} when t={:.3f})'.format(self.Who, self.Message, self.Address, self.When)

    def __str__(self):
        return 'Request:\t{} want to do {} in {} when t={:.3f}'.format(self.Who, self.Message, self.Address, self.When)

    def up_scale(self, adr):
        """
        Append upper address into address
        :param adr: upper position
        :return: extended request
        """
        new_adr = self.Where + [adr]
        return Request(self.Event, self.Who, new_adr)

    def down_scale(self):
        """
        Decrease scale of the request
        :return: upper address and reformed request
        """
        if self.reached():
            raise AttributeError('It is the lowest scale')
        new_adr = self.Where[:-1]
        return self.Where[-1], Request(self.Event, self.Who, new_adr)

    def reached(self):
        return len(self.Where) is 1

    def __gt__(self, ot):
        return self.When > ot.When

    def __le__(self, ot):
        return self.When <= ot.When

    def __eq__(self, ot):
        return self.When == ot.When


Request.NullRequest = Request(Event(None, float('inf')), 'Nobody', 'Nowhere')


def get_scheduler(loc, tp=None):
    tp = tp if tp else DefaultScheduler
    if tp == 'PriorityQueue':
        return PriorityQueueScheduler(loc)
    elif tp == 'Looping':
        return LoopingScheduler(loc)
    else:
        raise TypeError('Unknown scheduler type')


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
        try:
            self.Upcoming.remove(atom)
        except KeyError:
            return

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
        self.Queue = list()
        self.Waiting = set()

    def join_scheduler(self, atom):
        self.Waiting.add(atom)

    def leave_scheduler(self, atom):
        atom.drop_next()
        try:
            self.Waiting.remove(atom)
        except KeyError:
            pass

    def await(self, atom):
        self.Waiting.add(atom)
        self.pop_from_upcoming(atom)

    def reschedule_all(self):
        self.Upcoming.clear()
        self.OwnTime = float('Inf')

        self.Waiting.update(a for _, a, _ in self.Queue)
        self.Queue = list()
        self.reschedule_waiting()

    def reschedule_waiting(self):
        atoms = list(self.Waiting)
        for atom in atoms:
            event = atom.Next
            tte = event.Time
            entry = [tte, atom, event]
            heapq.heappush(self.Queue, entry)

            if tte < self.OwnTime:
                self.Upcoming.clear()
                self.OwnTime = float('Inf')

        self.Counter['Requeuing'] += len(self.Waiting)
        self.Waiting.clear()

        if len(self.Queue) > PriorityQueueScheduler.CAP * self.NumAtoms:
            print(len(self.Queue), min(self.Queue)[0], self.NumAtoms)
            self.clean_queue()

    def clean_queue(self):
        # queue = [[t, a, e] for t, a, e in self.Queue if not e.is_cancelled()]
        self.Queue = [[t, a, e] for t, a, e in self.Queue if not e.is_cancelled()]
        heapq.heapify(self.Queue)

    def find_upcoming_atoms(self):
        self.OwnTime = self.find_min_t()
        if self.OwnTime == float("inf"):
            return
        self.Upcoming.clear()

        while self.Queue:
            try:
                t, _, e = min(self.Queue)
                if e.is_cancelled():
                    heapq.heappop(self.Queue)

                if t is self.OwnTime:
                    t, a, e = heapq.heappop(self.Queue)
                    self.Waiting.add(a)
                    self.Upcoming.add(a)

                else:
                    return
            except (IndexError, KeyError):
                break

    def find_min_t(self):
        while self.Queue:
            t, _, e = min(self.Queue)
            if e.is_cancelled():
                heapq.heappop(self.Queue)
            else:
                return t
        else:
            return float('inf')
