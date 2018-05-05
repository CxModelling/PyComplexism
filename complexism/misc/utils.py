__author__ = 'TimeWz667'
__all__ = ['name_generator']


def name_generator(prefix, start, by):
    i = int(start)
    by = int(by) if by >= 1 else by

    while True:
        yield '{}{}'.format(prefix, i)
        i += by
