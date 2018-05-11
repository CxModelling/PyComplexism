__author__ = 'TimeWz667'


__all__ = ['Trigger', 'EventTrigger',
           'AttributeTrigger', 'AttributeEnterTrigger', 'AttributeExitTrigger',
           'ForeignTrigger', 'ForeignSetTrigger']


class Trigger:
    NullTrigger = None

    def check_event(self, ag, evt):
        return False

    def check_pre_change(self, ag):
        return False

    def check_post_change(self, ag):
        return False

    def check_change(self, pre, post):
        return False

    def check_enter(self, ag):
        return False

    def check_exit(self, ag):
        return False

    def check_foreign(self, model, loc=None):
        return False


Trigger.NullTrigger = Trigger()


class EventTrigger(Trigger):
    def __init__(self, todo):
        self.Todo = todo

    def check_event(self, ag, evt):
        return self.Todo == evt.Todo


class AttributeTrigger(Trigger):
    def __init__(self, attributes):
        self.Attributes = dict(attributes)

    def __check(self, ag):
        for k, v in self.Attributes:
            try:
                if ag[k] != v:
                    return False
            except KeyError:
                return False
        return True

    def check_pre_change(self, ag):
        return self.__check(ag)

    def check_post_change(self, ag):
        return self.__check(ag)

    def check_change(self, pre, post):
        return pre ^ post

    def check_enter(self, ag):
        return self.__check(ag)

    def check_exit(self, ag):
        return self.__check(ag)


class AttributeEnterTrigger(Trigger):
    def __init__(self, attributes):
        self.Attributes = dict(attributes)

    def __check(self, ag):
        for k, v in self.Attributes:
            try:
                if ag[k] != v:
                    return False
            except KeyError:
                return False
        return True

    def check_pre_change(self, ag):
        return self.__check(ag)

    def check_post_change(self, ag):
        return self.__check(ag)

    def check_change(self, pre, post):
        return (not pre) and post

    def check_enter(self, ag):
        return self.__check(ag)


class AttributeExitTrigger(Trigger):
    def __init__(self, attributes):
        self.Attributes = dict(attributes)

    def __check(self, ag):
        for k, v in self.Attributes:
            try:
                if ag[k] != v:
                    return False
            except KeyError:
                return False
        return True

    def check_pre_change(self, ag):
        return self.__check(ag)

    def check_post_change(self, ag):
        return self.__check(ag)

    def check_change(self, pre, post):
        return pre and (not post)

    def check_exit(self, ag):
        return self.__check(ag)


class ForeignTrigger(Trigger):
    def __init__(self, model=None, loc=None):
        self.Model = model
        self.Location = loc

    def append(self, model, loc):
        self.Model = model
        self.Location = loc

    def check_foreign(self, model, loc=None):
        if self.Model != model.Name:
            return False
        if not loc:
            return True
        return loc == self.Location


class ForeignSetTrigger(Trigger):
    def __init__(self, mps=None):
        self.Models = dict(mps) if isinstance(mps, dict) else dict()

    def append(self, model, loc):
        self.Models[model] = loc

    def check_foreign(self, model, loc=None):
        try:
            location = self.Models[model]
            if not loc:
                return True
            return loc == location
        except KeyError:
            return False
