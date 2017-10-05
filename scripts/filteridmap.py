#!/usr/bin/env python

# Filter ID mapping to given subset of IDs.


from __future__ import print_function

import sys
import logging

from logging import info

from common import read_mapping, read_ids


logging.getLogger().setLevel(logging.INFO)


def argparser():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('-r', '--reverse', default=False, action='store_true',
                    help='Reverse IDs in mapping')
    ap.add_argument('mapping', metavar='FILE', help='ID mapping')
    ap.add_argument('ids', metavar='FILE', help='IDs to filter to')
    return ap


def filter_mapping(mapping, ids):
    filtered, removed = [], 0
    for id1, id_type, id2 in mapping:
        if id1 in ids:
            filtered.append((id1, id_type, id2))
        else:
            removed += 1
    info('Filtered to {} (removed {})'.format(len(filtered), removed))
    return filtered


def main(argv):
    args = argparser().parse_args(argv[1:])
    ids = set(read_ids(args.ids))
    mapping = read_mapping(args.mapping, args.reverse)
    filtered = filter_mapping(mapping, ids)
    for m in filtered:
        print('\t'.join(m))


if __name__ == '__main__':
    sys.exit(main(sys.argv))
