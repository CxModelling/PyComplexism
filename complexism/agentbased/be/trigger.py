__author__ = 'TimeWz667'


__all__ = ['Trigger', 'EventTrigger',
           'AttributeTrigger', 'AttributeEnterTrigger', 'AttributeExitTrigger']


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
