from itertools import groupby
import heapq
from enum import Enum, auto
from .event import Event

__author__ = 'TimeWz667'
__all__ = ['Disclosure', 'Request', 'Schedule']


class Disclosure:
    def __init__(self, what, who, where, **kwargs):
        self.What = what
        self.Who = who
        self.Where = [where] if isinstance(where, str) else where
        self.Arguments = dict(kwargs)

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


class Schedule:
    def __init__(self, loc):
        self.Location = loc

        self.Requests = list()
        self.Disclosures = list()
        self.Time = float('inf')
        self.OwnTime = float('inf')

        self.Queue = list()
        self.WaitingActors = set()
        self.CurrentRequests = dict()

    def add_actor(self, actor):
        self.WaitingActors.add(actor)
        actor.set_scheduler(self)

    def remove_actor(self, actor):
        actor.drop_next()
        actor.detach_scheduler()
        try:
            self.WaitingActors.remove(actor)
        except KeyError:
            pass

    def reschedule_actor(self, actor):
        event = actor.Next
        tte = event.Time
        entry = [tte, actor, event]
        heapq.heappush(self.Queue, entry)
        if tte < self.OwnTime:
            self.put_requests_back()

    def add_schedule_actor(self, actor):
        self.add_actor(actor)
        self.reschedule_actor(actor)

    def reschedule_all_actors(self):
        self.WaitingActors.update(a for _, a, _ in self.Queue)
        self.Queue = list()
        self.reschedule_waiting_actors()

    def reschedule_waiting_actors(self):
        for actor in self.WaitingActors:
            self.reschedule_actor(actor)
        self.WaitingActors.clear()

    def requeue_actor(self, actor):
        self.WaitingActors.add(actor)

    def find_min_t(self):
        while self.Queue:
            t, _, e = min(self.Queue)
            if e.is_cancelled():
                heapq.heappop(self.Queue)
            else:
                return t
        else:
            return float('inf')

    def extract_nearest(self):
        while self.Queue:
            try:
                t = self.find_min_t()
                if t <= self.OwnTime:
                    t, a, e = heapq.heappop(self.Queue)
                    self.requeue_actor(a)
                    self.CurrentRequests[a] = Request(e, a.Name, self.Location)
                    self.OwnTime = e.Time
                else:
                    break
            except (IndexError, KeyError):
                break

    def put_requests_back(self):
        for a, r in self.CurrentRequests.items():
            e = r.Event

            if e.is_cancelled():
                self.reschedule_actor(a)
            else:
                self.reschedule_actor(a)
        self.CurrentRequests = dict()
        self.OwnTime = float('inf')

    def __gt__(self, ot):
        return self.Time > ot.Time

    def __le__(self, ot):
        return self.Time <= ot.Time

    def __eq__(self, ot):
        return self.Time == ot.Time

    def __len__(self):
        return len(self.Requests) + len(self.Disclosures)

    def __iter__(self):
        return iter(self.Disclosures + self.Requests)

    # Collection stage
    def find_next(self):
        self.reschedule_waiting_actors()
        if not self.CurrentRequests:
            self.extract_nearest()
        self.Requests = list(self.CurrentRequests.values())
        self.Time = min(self.Time, self.OwnTime)

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

    def is_executable(self):
        return self.Time is self.OwnTime

    def pop_disclosures(self):
        ds, self.Disclosures = self.Disclosures, list()
        return ds

    def fetch_disclosures(self, ds):
        self.Disclosures = ds

    def execution_completed(self):
        self.Requests.clear()
        self.CurrentRequests = dict()
        self.OwnTime = float('inf')

    def cycle_completed(self):
        self.Disclosures.clear()
        self.Time = min(float('inf'), self.OwnTime)

    def is_empty(self):
        return not self.Requests

    def __repr__(self):
        return 'Req: {}, Dss: {}, Next Event Time: {}'.format(len(self.Requests), len(self.Disclosures), self.Time)

    def print(self):
        print(self.Location, ':', repr(self))
