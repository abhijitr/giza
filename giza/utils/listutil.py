# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

import itertools


def first(iterable, default=None):
    for x in iterable:
        return x
    return default


def uniqify(iterable, key=None):
    """Takes an iterable and returns a uniqified list, preserving order. 

    :param key: a lambda that returns an item's object identity"""

    seen = set()
    seen_add = seen.add

    if not key:
        return [x for x in iterable if x not in seen and not seen_add(x)]

    return [x for x in iterable if key(x) not in seen and not seen_add(key(x))]


def dictify(iterable, key_func):
    d = {key_func(item):item for item in iterable}
    return d

def dictify_named_tuple(named_tuple): 
    return dict((s, getattr(named_tuple, s)) for s in named_tuple._fields) 

def listify(iterable_or_singleton):
    """ No-op if it's an iterable, otherwise wraps the given object in a list
    """

    if (hasattr(iterable_or_singleton, '__iter__') and
            not isinstance(iterable_or_singleton, dict)):
        return iterable_or_singleton

    return [iterable_or_singleton]


def chunkify(iterable, chunk_size):
    """ Break up an iterable into chunks of size chunk_size.
    """
    if chunk_size <= 0:
        raise ValueError('chunk_size must be a positive integer')

    i = 0
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []

    if len(chunk):
        yield chunk


def groupby(iterable, group_func):
    temp = sorted(iterable, key=group_func)

    group_iter = itertools.groupby(temp, group_func)

    groups = [(group_id, list(group)) for group_id, group in group_iter]

    return groups


def countby(iterable, group_func):
    groups = groupby(iterable, group_func)

    counts = [(group_id, len(group)) for group_id, group in groups]

    return sorted(counts, key=lambda x: x[1])


def weave(*iterables):
    """ Cycle through the 0th item in each iterable, then 
        the 1st item in each iterable, and so on to exhaustion """

    remaining = [iterable.__iter__() for iterable in iterables]
    remaining_count = len(remaining)
    while True:
        for i in range(len(remaining)):
            iterator = remaining[i]
            if not iterator:
                continue

            try:
                next_value = iterator.next()
            except StopIteration:
                remaining[i] = None
                remaining_count -= 1
                continue

            yield next_value

        if remaining_count == 0:
            break

    return


def flatten(iter_of_iters):
    return list(itertools.chain(*iter_of_iters))