#!/usr/bin/env python

# Apply ID mapping to given list of IDs.


from __future__ import print_function

import sys
import logging

from collections import defaultdict
from logging import info, warn

from common import read_mapping, read_ids


logging.getLogger().setLevel(logging.INFO)


def argparser():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('-e', '--echo', default=False, action='store_true',
                    help='Echo original ID in output')
    ap.add_argument('-r', '--reverse', default=False, action='store_true',
                    help='Reverse IDs in mapping')
    ap.add_argument('mapping', metavar='FILE', help='ID mapping')
    ap.add_argument('ids', metavar='FILE', help='IDs to map')
    return ap


def to_dict(mapping):
    dict_ = defaultdict(list)
    for id1, id_type, id2 in mapping:
        dict_[id1].append((id_type, id2))
    return dict_


def main(argv):
    args = argparser().parse_args(argv[1:])
    ids = read_ids(args.ids)
    mapping = read_mapping(args.mapping, args.reverse)
    mapping = to_dict(mapping)
    found, missing = 0, 0
    output = sys.stdout.write
    for id_ in ids:
        if args.echo:
            output('{}\t'.format(id_))
        if id_ in mapping:
            mapped = [id2 for type_, id2 in mapping[id_]]
            found += 1
            output(' '.join(mapped))
        else:
            warn('no mapping for {}'.format(id_))
            missing += 1
            output(id_)
        output('\n')
    info('found {} ids, missing {}'.format(found, missing))


if __name__ == '__main__':
    sys.exit(main(sys.argv))
