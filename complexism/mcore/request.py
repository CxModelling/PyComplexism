__author__ = 'TimeWz667'


class Request:
    NullRequest = None

    def __init__(self, evt, ti, nod='', adr=None):
        """

        :param adr: the address of node with event
        :param nod: name of the node
        :param evt: event in String
        :param time: event time
        """
        self.Address = adr if adr else nod
        self.Node = nod
        self.Event = evt
        self.Time = ti

    def __repr__(self):
        return '{}, {}, {:.4f}'.format(self.Address, self.Event, self.Time)

    def up(self, adr):
        """
        Append upper address into address
        :param adr: upper position
        :return: extended request
        """
        new_adr = '{}@{}'.format(adr, self.Address)
        return Request(self.Event, self.Time, self.Node, new_adr)

    def down(self):
        """
        Decrease scale of the request
        :return: reformed request
        """
        ad, new_adr = self.Address.split('@', 1)
        return ad, Request(self.Event, self.Time, self.Node, new_adr)

    def reached(self):
        return self.Address.find('@') < 0

    def __gt__(self, ot):
        return self.Time > ot.Time

    def __le__(self, ot):
        return self.Time <= ot.Time

    def __eq__(self, ot):
        return self.Time == ot.Time


Request.NullRequest = Request('', float('inf'))


class RequestSingle:
    def __init__(self):
        self.Request = Request.NullRequest
        self.Time = float('inf')

    def __repr__(self):
        return '{} Event, {:.4f}'.format(self.Request, self.Time)

    def up(self, adr):
        return self.Request.up(adr)

    def pop_lower_requests(self):
        if self.Request.reached():
            return
        else:
            req = self.Request
            self.clear()
        return req

    def clear(self):
        self.Request, self.Time = Request.NullRequest, self.Time = float('inf')

    def __len__(self):
        return 1

    def __iter__(self):
        return iter([self.Request])

    def append(self, evt):
        if evt.Time < self.Time:
            self.Request = evt
            self.Time = evt.Time

    def add(self, evt):
        if evt.Time < self.Time:
            self.Request = evt

    def __gt__(self, ot):
        return self.Time > ot.Time

    def __le__(self, ot):
        return self.Time <= ot.Time

    def is_empty(self):
        return self.Request is Request.NullRequest


class RequestSet:
    def __init__(self):
        self.Requests = list()
        self.Time = float('inf')

    def __repr__(self):
        return '{} Event, {:.4f}'.format(len(self), self.Time)

    def up(self, adr):
        return [evt.up(adr) for evt in self.Requests]

    def pop_lower_requests(self):
        lower = [req for req in self.Requests if not req.reached()]
        self.Requests = [req for req in self.Requests if req.reached()]
        if (not self.Requests) and (not lower):
            self.Time = float('inf')
        return lower

    def clear(self):
        self.Requests = list()
        self.Time = float('inf')

    def __len__(self):
        return len(self.Requests)

    def __iter__(self):
        return iter(self.Requests)

    def append(self, res):
        if res.Time < self.Time:
            self.Requests = [res]
            self.Time = res.Time
        elif res.Time == self.Time:
            self.Requests.append(res)

    def append_src(self, ag, evt, ti):
        if ti < self.Time:
            self.Requests = [Request(evt, ti, ag)]
            self.Time = ti
        elif ti == self.Time:
            self.Requests.append(Request(evt, ti, ag))

    def add(self, evts):
        ti = evts[0].Time
        if ti < self.Time:
            self.Requests = evts
            self.Time = ti
        elif ti == self.Time:
            self.Requests += evts

    def merge(self, es, ag_id=''):
        if es.Time < self.Time:
            self.Requests = es.up(ag_id)
            self.Time = es.Time
        elif es.Time == self.Time:
            self.Requests += es.up(ag_id)

    def __gt__(self, ot):
        return self.Time > ot.Time

    def __le__(self, ot):
        return self.Time <= ot.Time

    def is_empty(self):
        return not self.Requests


if __name__ == '__main__':
    evt1 = Request('EvtA', 1.12345, 'N1', 'A')
    evt2 = Request('EvtB', 1.2345, 'N1', 'B')
    print(evt1)
    evt3 = evt1.up('B')
    print(evt3)
    min(evt1, evt2)
    print((evt1 == evt2) is False)
    print((evt1 < evt2) is True)
    print((evt1 <= evt2) is True)
    print((evt1 > evt2) is False)
    print((evt1 >= evt2) is False)
    print((evt1 != evt2) is True)

    es1 = RequestSet()
    print(es1, es1.is_empty())
    es1.append(evt1)
    print(es1, es1.is_empty())
    es1.append(Request('E', 1.12345, 'N', 'A'))
    print(es1)

    es2 = RequestSet()
    es2.append(Request('E', 1.12, 'N', 'A'))
    es1.merge(es2)
    print(es1)
    es3 = RequestSet()
    es3.append(Request('E', 1.12, 'N', 'A'))
    es3.append(Request('E', 1.12, 'N', 'A'))
    es1.merge(es3)
    print(es1)
