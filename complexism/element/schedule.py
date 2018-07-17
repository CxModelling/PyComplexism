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


class Status(Enum):
    TO_COLLECT = auto()  # collect
    TO_VALIDATE = auto()
    TO_EXECUTE = auto()
    TO_FINISH = auto()


class Schedule:
    def __init__(self, loc):
        self.Location = loc
        self.Requests = list()
        self.Disclosures = list()
        self.Time = float('inf')
        self.Status = Status.TO_COLLECT

        self.Actors = dict()
        self.WaitingActors = list()
        self.Queue = list()

    def add_actor(self, actor):
        self.Actors[actor] = None
        self.WaitingActors.append(actor)

    def remove_actor(self, actor):
        try:
            self.Actors[actor][-1].cancel()
            del self.Actors[actor]
            self.WaitingActors.remove(actor)
        except (KeyError, ValueError):
            pass

    def reschedule_actor(self, actor, ti):
        try:
            self.Actors[actor][-1].cancel()
        except TypeError:
            pass

        actor.update_time(ti)
        event = actor.Next
        tte = event.Time
        entry = [tte, actor, event]
        self.Actors[actor] = entry
        heapq.heappush(self.Queue, entry)

        try:
            self.WaitingActors.remove(actor)
        except ValueError:
            pass

    def add_schedule_actor(self, actor, ti):
        self.Actors[actor] = None
        self.reschedule_actor(actor, ti)

    def reschedule_all_actors(self, ti):
        self.Queue = list()
        for actor, entry in self.Actors.items():
            self.reschedule_actor(actor, ti)
        self.WaitingActors = list()

    def reschedule_waiting_actors(self, ti):
        while self.WaitingActors:
            actor = self.WaitingActors.pop()
            self.reschedule_actor(actor, ti)

    def clean_cancelled(self):
        self.Queue = [q for q in self.Queue if not q[-1].is_cancelled()]

    def pop_event(self):
        while self.Queue:
            tte, actor, event = heapq.heappop(self.Queue)
            if actor.Next is not event:  # if the next event have been updated
                event.cancel()

            if not event.is_cancelled():
                self.WaitingActors.append(actor)
                return actor, event

            if actor in self.WaitingActors:
                self.reschedule_actor(actor, tte)
        raise KeyError('pop from an empty priority queue')

    def remove_event_until(self, ti):
        while self.Queue:
            tte = self.Queue[0][0]
            if tte > ti:
                return

            tte, actor, event = heapq.heappop(self.Queue)

            if actor not in self.Actors:
                continue

            _, _, e = self.Actors[actor]
            if event is e:
                self.reschedule_actor(actor, ti)

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
        try:
            ti, actor, event = min(self.Queue)
            if ti < self.Time:
                self.Requests = [Request(e, a.Name, self.Location) for t, a, e in self.Queue if t is ti]
                self.Time = ti
        except ValueError:
            pass

    def append_request_from_source(self, event, who):
        self.Requests.append(Request(event, who, self.Location))

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
        ti = lower.Time
        if ti < self.Time:
            if lower.Requests:
                self.Requests = lower.up_scale_requests(self.Location)
            self.Time = ti
        elif ti == self.Time:
            if self.Requests:
                self.Requests += lower.up_scale_requests(self.Location)
        else:
            return

    # After sending back

    def fetch_requests(self, rs):
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

        if (not self.Requests) and (not lower):
            self.execution_completed()

        return pop

    def pop_disclosures(self):
        ds, self.Disclosures = self.Disclosures, list()
        return ds

    def fetch_disclosures(self, ds):
        self.Disclosures = ds

    def waiting_for_collection(self):
        return self.Status is Status.TO_COLLECT

    def waiting_for_validation(self):
        return self.Status is Status.TO_VALIDATE

    def waiting_for_execution(self):
        return self.Status is Status.TO_EXECUTE

    def waiting_for_finish(self):
        return self.Status is Status.TO_FINISH

    def collection_completed(self):
        self.Status = Status.TO_VALIDATE

    def validation_completed(self):
        if self.is_empty():
            self.execution_completed()
        else:
            self.Status = Status.TO_EXECUTE

    def execution_completed(self):
        self.Status = Status.TO_FINISH
        self.Requests.clear()
        self.remove_event_until(self.Time)
        self.reschedule_waiting_actors(self.Time)
        self.Time = float('inf')

    def cycle_completed(self):
        self.Status = Status.TO_COLLECT
        self.Disclosures.clear()
        if self.Requests:
            self.Requests.clear()
            self.remove_event_until(self.Time)
            self.reschedule_waiting_actors(self.Time)
        self.Time = float('inf')

    def cycle_broke(self):
        self.cycle_completed()
        self.collection_completed()

    def is_empty(self):
        return not self.Requests

    def __repr__(self):
        return 'Status: {}, Req: {}, Dss: {}, Next Event Time: {}'.format(
            self.Status,
            len(self.Requests), len(self.Disclosures), self.Time)

    def print(self):
        print(self.Location, ':', repr(self))
