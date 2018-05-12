from complexism.agentbased.be import Trigger
__author__ = 'TimeWz667'


__all__ = ['TransitionTrigger',
           'StateTrigger', 'StateEnterTrigger', 'StateExitTrigger']


class TransitionTrigger(Trigger):
    def __init__(self, tr):
        self.Transition = tr

    def check_event(self, ag, evt):
        return self.Transition == evt.Todo


class StateTrigger(Trigger):
    def __init__(self, st):
        self.State = st

    def __check(self, ag):
        return self.State in ag

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


class StateEnterTrigger(Trigger):
    def __init__(self, st):
        self.State = st

    def __check(self, ag):
        return self.State in ag

    def check_pre_change(self, ag):
        return self.__check(ag)

    def check_post_change(self, ag):
        return self.__check(ag)

    def check_change(self, pre, post):
        return (not pre) and post

    def check_enter(self, ag):
        return self.__check(ag)


class StateExitTrigger(Trigger):
    def __init__(self, st):
        self.State = st

    def __check(self, ag):
        return self.State in ag

    def check_pre_change(self, ag):
        return self.__check(ag)

    def check_post_change(self, ag):
        return self.__check(ag)

    def check_change(self, pre, post):
        return pre and (not post)

    def check_exit(self, ag):
        return self.__check(ag)
