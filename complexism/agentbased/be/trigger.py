__author__ = 'TimeWz667'


__all__ = ['Trigger', 'EventTrigger',
           'AttributeTrigger', 'AttributeEnterTrigger', 'AttributeExitTrigger',
           'ForeignTrigger']


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
    def __init__(self, model=None, msg=None):
        self.Model = model
        if not msg:
            self.Messages = []
        elif isinstance(msg, list):
            self.Messages = msg
        else:
            self.Messages = [str(msg)]

    def add_source(self, model, msg):
        if self.Model == model:
            if isinstance(msg, str):
                self.Messages.append(msg)
            elif isinstance(msg, list):
                self.Messages += msg
        else:
            self.Model = model
            self.Messages = msg if isinstance(msg, list) else [msg]

    def check_foreign(self, model, msg='update'):
        if self.Model != model.Name:
            return False
        if msg == 'update':
            return True
        return msg in self.Messages
