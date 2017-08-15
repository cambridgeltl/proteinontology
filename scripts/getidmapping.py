#!/usr/bin/env python

# Extract mapping to UniProt IDs from Protein Ontology in OBO Graphs
# JSON-LD format.


from __future__ import print_function

import sys
import json

from logging import warn


def argparser():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('files', metavar='FILE', nargs='+',
                    help='Input PubTator files')
    return ap


class FormatError(Exception):
    pass


def pretty_dumps(obj):
    return json.dumps(obj, sort_keys=True, indent=2, separators=(',', ': '))


def assure_list(obj):
    return obj if isinstance(obj, list) else [obj]


def is_proteinontology_node(node):
    id_ = node['id']
    return id_.startswith('PR:')


def get_xrefs(meta):
    if 'xrefs' not in meta:
        return []
    xrefs, vals = assure_list(meta['xrefs']), []
    for xref in xrefs:
        vals.append(xref['val'])
    return vals


def uniprot_ids(ids):
    prefix = 'UniProtKB:'
    filtered = []
    for id_ in ids:
        if id_.startswith(prefix):
            filtered.append(id_[len(prefix):])
    return filtered


def process_node(node):
    metas = assure_list(node['meta'])
    if len(metas) != 1:
        raise FormatError('expected one meta, got {}'.format(len(metas)))
    meta = metas[0]
    xrefs = get_xrefs(meta)
    uids = uniprot_ids(xrefs)
    if len(uids) > 1:
        warn('multiple UniProt IDs for {}: {}'.format(node['id'], uids))
    for uid in uids:
        print('{}\tPRO\t{}'.format(uid, node['id']))


def process_graph(graph):
    nodes = assure_list(graph['nodes'])
    for node in nodes:
        if not is_proteinontology_node(node):
            continue    # skip imported from other ontologies
        process_node(node)


def process(fn):
    with open(fn) as f:
        data = json.load(f)
    graphs = assure_list(data['graphs'])
    for graph in graphs:
        process_graph(graph)


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.files:
        process(fn)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
