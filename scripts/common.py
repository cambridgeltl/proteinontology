from __future__ import print_function

import re

from logging import info


class FormatError(Exception):
    pass


def read_mapping(fn, reverse=False):
    """Read ID mapping."""
    read = 0
    mapping = []
    with open(fn) as f:
        for i, l in enumerate(f, start=1):
            l = l.rstrip('\n')
            f = l.split('\t')
            if len(f) != 3:
                raise FormatError('expected 3 TAB-separated values, got {} on line {} in {}: {}'.format(len(f), i, fn, l))
            id1, id_type, id2 = f
            if reverse:
                id1, id2 = id2, id1
            mapping.append((id1, id_type, id2))
            read += 1
    info('Read {} mappings from {}'.format(read, fn))
    return mapping


def read_ids(fn):
    ids = list()
    with open(fn) as f:
        for i, l in enumerate(f, start=1):
            l = l.rstrip()
            m = re.match(r'^\S+$', l)
            if not m:
                raise FormatError('Expected ID, got {}: line {} in {}'.format(
                    l, i, fn))
            ids.append(l)
    info('Read {} ids from {}'.format(len(ids), fn))
    return ids
