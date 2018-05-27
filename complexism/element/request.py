from .event import Event
from itertools import groupby

__author__ = 'TimeWz667'
__all__ = ['Request', 'RequestSet']


class Request:
    NullRequest = None

    def __init__(self, evt: Event, who='Someone', where='Somewhere'):
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
    def Time(self):
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
        return 'Request({} does {} at {} as {:.3f})'.format(self.Who, self.Message, self.Address, self.When)

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
