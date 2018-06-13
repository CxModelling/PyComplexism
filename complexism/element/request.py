from .event import Event
from itertools import groupby
from enum import Enum, auto

__author__ = 'TimeWz667'
__all__ = ['Exposure', 'Request', 'Schedule']


class Exposure:
    def __init__(self, what, who, where):
        self.What = what
        self.Who = who
        self.Where = where

    def up_scale(self, adr):
        """
        Append upper address into address
        :param adr: upper position
        :return: extended request
        """
        new_adr = self.Where + [adr]
        return Exposure(self.What, self.Who, new_adr)

    def down_scale(self):
        """
        Decrease scale of the request
        :return: upper address and reformed request
        """
        if self.reached():
            raise AttributeError('It is the lowest scale')
        new_adr = self.Where[:-1]
        return self.Where[-1], Exposure(self.What, self.Who, new_adr)

    def reached(self):
        return len(self.Where) <= 2

    def __repr__(self):
        return 'Exposure({} did {} at {})'.format(self.Who, self.What, self.Where)


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

    def __repr__(self):
        return 'Request({} want to do {} at {} when {:.3f})'.format(self.Who, self.Message, self.Address, self.When)

    def pop_request(self, adr):
        """
        Append upper address into address
        :param adr: upper position
        :return: extended request
        """
        new_adr = self.Where + [adr]
        return Request(self.Event, self.Who, new_adr)

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


Request.NullRequest = Request(Event.NullEvent, 'Nobody', 'Nowhere')


class RequestSet:
    def __init__(self):
        self.Requests = list()
        self.Time = float('inf')

    def __repr__(self):
        return '{} Event at {:.4f}'.format(len(self), self.Time)

    def up_scale(self, adr):
        return [req.up_scale(adr) for req in self.Requests]

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
            self.Time = float('inf')

        return pop

    def clear(self):
        self.Requests = list()
        self.Time = float('inf')

    def __len__(self):
        return len(self.Requests)

    def __iter__(self):
        return iter(self.Requests)

    def append_request(self, req):
        ti = req.Time
        if ti < self.Time:
            self.Requests = [req]
            self.Time = ti
        elif ti == self.Time:
            self.Requests.append(req)

    def append_event(self, evt, who, where):
        ti = evt.Time
        if evt.Time < self.Time:
            self.Requests = [Request(evt, who, where)]
            self.Time = evt.Time
        elif ti == self.Time:
            self.Requests.append(Request(evt, who, where))

    def append_requests(self, reqs):
        ti = reqs[0].Time
        if ti < self.Time:
            self.Requests = list(reqs)
            self.Time = ti
        elif ti == self.Time:
            self.Requests += reqs

    def merge_lower(self, rs, loc='Here'):
        ti = rs.Time
        if ti < self.Time:
            self.Requests = rs.up_scale(loc)
            self.Time = rs.Time
        elif rs.Time == self.Time:
            self.Requests += rs.up_scale(loc)

    def __gt__(self, ot):
        return self.Time > ot.Time

    def __le__(self, ot):
        return self.Time <= ot.Time

    def __eq__(self, ot):
        return self.Time == ot.Time

    def is_empty(self):
        return not self.Requests


class Status(Enum):
    TO_COLLECT = auto()  # collect
    TO_VALIDATE = auto()
    TO_EXECUTE = auto()


class Schedule:
    def __init__(self, loc):
        self.Location = loc
        self.RequestList = list()
        self.ExposureList = list()
        self.Time = float('inf')
        self.Status = Status.TO_COLLECT

    def __gt__(self, ot):
        return self.Time > ot.Time

    def __le__(self, ot):
        return self.Time <= ot.Time

    def __eq__(self, ot):
        return self.Time == ot.Time

    def __len__(self):
        return len(self.RequestList) + len(self.ExposureList)

    def __iter__(self):
        return iter(self.ExposureList + self.RequestList)

    def append_request(self, req: Request):
        """
        Append a request
        :param req: request to be execute
        :return: true if the request is the nearest
        """
        ti = req.When
        if ti < self.Time:
            self.RequestList = [req]
            self.Time = ti
            return True
        elif ti == self.Time:
            self.RequestList.append(req)
            return True
        return False

    def append_request_from_source(self, event, who):
        req = Request(event, who, self.Location)
        return self.append_request(req)

    def append_exposure(self, exp):
        """
        Append an exposure
        :param exp: message to be exposed
        """
        self.ExposureList.append(exp)

    def up_scale(self, loc):
        r = [req.up_scale(loc) for req in self.RequestList]
        e = [exp.up_scale(loc) for exp in self.ExposureList]
        return r, e

    def append_lower_schedule(self, lower):
        ti = lower.Time
        if ti < self.Time:
            r, e = lower.up_scale(self.Location)
            self.RequestList = r
            self.ExposureList = e
            self.Time = ti
        elif ti == self.Time:
            r, e = lower.up_scale(self.Location)
            self.RequestList += r
            self.ExposureList += e

    def approve(self, req_set, exp_set):
        pass

    def _pass_down_approved(self):
        pass

    def disapprove(self, req_set, exp_set):
        pass

    def _pass_down_disapproved(self):
        pass

    def collection_completed(self):
        self.Status = Status.TO_VALIDATE

    def validation_completed(self):
        if self.is_empty():
            self.execution_completed()
        else:
            self.Status = Status.TO_EXECUTE

    def execution_completed(self):
        self.Status = Status.TO_COLLECT
        self.ExposureList.clear()
        self.RequestList.clear()
        self.Time = float('inf')

    def is_empty(self):
        return not self.RequestList and not self.ExposureList

    def __repr__(self):
        return 'Status: {}, Req: {}, Exp: {}, Next Event Time: {}'.format(
            self.Status,
            len(self.RequestList), len(self.ExposureList), self.Time)
