#!/usr/bin/env python

# Extract mapping to UniProt IDs from Protein Ontology in OBO Graphs
# JSON-LD format.


from __future__ import print_function

import sys
import json

from collections import defaultdict
from logging import info, warn


def argparser():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--include-deprecated', default=False,
                    action='store_true', help='Include deprecated terms')
    ap.add_argument('-g', '--generalize', default=False, action='store_true',
                    help='Generalize PRO IDs to "Category=gene" level')
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


def is_deprecated(node):
    meta = get_meta(node)
    return meta.get('deprecated') is True


def get_meta(node):
    metas = assure_list(node['meta'])
    if len(metas) != 1:
        raise FormatError('expected one meta, got {}'.format(len(metas)))
    return metas[0]


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


def has_category(node, category):
    """Return True if node has given category, False otherwise."""
    category_string = 'Category={}.'.format(category)
    meta = get_meta(node)
    for c in assure_list(meta.get('comments', [])):
        if c.startswith(category_string):
            return True
    return False


def nearest_ancestors(node, graph, category):
    """Return list of nearest ancestors with given category."""
    id_ = node['id']
    cache = nearest_ancestors.cache[id(graph)][category]
    if id_ not in cache:
        if has_category(node, category):
            cache[id_] = [node]    # already at gene level
        else:
            parents_ancestors, seen = [], set()
            for parent in graph.parents(node):
                for ancestor in nearest_ancestors(parent, graph, category):
                    if ancestor['id'] not in seen:
                        parents_ancestors.append(ancestor)
                        seen.add(ancestor['id'])
            cache[id_] = parents_ancestors
    return cache[id_]
nearest_ancestors.cache = defaultdict(lambda: defaultdict(lambda :defaultdict(list)))


def furthest_ancestors(node, graph, category):
    """Return list of most distant ancestors with given category."""
    id_ = node['id']
    cache = furthest_ancestors.cache[id(graph)][category]
    if id_ not in cache:
        parents_ancestors, seen = [], set()
        for parent in graph.parents(node):
            for ancestor in furthest_ancestors(parent, graph, category):
                if ancestor['id'] not in seen:
                    parents_ancestors.append(ancestor)
                    seen.add(ancestor['id'])
        if parents_ancestors:
            cache[id_] = parents_ancestors    # more distant in category
        elif has_category(node, category):
            cache[id_] = [node]    # node is most distant
        else:
            cache[id_] = []    # no ancestors in category
    return cache[id_]
furthest_ancestors.cache = defaultdict(lambda: defaultdict(lambda :defaultdict(list)))


def generalize_to_gene(node, graph, options):
    """Return nearest ancestor with "Category=gene" in the graph.

    If no ancestor has "Category=gene", return ancestor with
    "Category=organism-gene".

    Maps e.g. PR:P04637 "cellular tumor antigen p53 (human)" and
    PR:P02340 "cellular tumor antigen p53 (mouse)" to
    PR:000003035 "cellular tumor antigen p53".
    """
    generalized = nearest_ancestors(node, graph, 'gene')
    if not generalized:
        generalized = nearest_ancestors(node, graph, 'organism-gene')
    if not generalized:
        info('no gene ancestors: {}'.format(node))
        return node
    elif len(generalized) == 1:
        if generalized[0]['id'] == node['id']:
            info('not generalized: {}'.format(node))
        else:
            info('generalized {} to {}'.format(node, generalized[0]))
        return generalized[0]
    else:
        assert(len(generalized)) > 1, 'internal error'
        warn('generalized to multiple, arbitrarily taking first: {} -> {}'.format(node['id'], ', '.join(str(g) for g in generalized)))
        return generalized[0]


def process_node(node, graph, options):
    meta = get_meta(node)
    xrefs = get_xrefs(meta)
    uids = uniprot_ids(xrefs)
    if len(uids) > 1:
        warn('multiple UniProt IDs for {}: {}'.format(node['id'], uids))
    if options.generalize:
        node = generalize_to_gene(node, graph, options)
    for uid in uids:
        print('{}\tPRO\t{}'.format(uid, node['id']))


class OboGraphNode(dict):
    """Node in OBO Graph"""

    def __init__(self, *args, **argv):
        dict.__init__(self, *args, **argv)

    def __str__(self):
        return '{} ({})'.format(self['id'], self['lbl'])


class OboGraph(dict):
    """OBO Graph"""

    def __init__(self, *args, **argv):
        dict.__init__(self, *args, **argv)
        # lazy init
        self._node_by_id = None
        self._is_a = None

    def nodes(self):
        for node in assure_list(self.get('nodes', [])):
            yield OboGraphNode(node)

    def get_node(self, id_):
        if self._node_by_id is None:
            self_analyze()
        return self._node_by_id[id_]

    def parents(self, node):
        if self._is_a is None:
            self._analyze()
        id_ = node['id']
        return [self.get_node(p) for p in self._is_a[id_]]

    def _analyze(self):
        self._analyze_nodes()
        self._analyze_edges()

    def _analyze_nodes(self):
        self._node_by_id = {}
        for node in self.nodes():
            id_ = node['id']
            if id_ in self._node_by_id:
                raise FormatError('duplicate id {}'.format(id_))
            self._node_by_id[id_] = node

    def _analyze_edges(self):
        self._is_a = defaultdict(list)
        edges = assure_list(self.get('edges', []))
        for edge in edges:
            sub, pred, obj = edge['sub'], edge['pred'], edge['obj']
            if pred == 'is_a':
                self._is_a[sub].append(obj)


def process_graph(graph, options):
    graph = OboGraph(graph)
    for node in graph.nodes():
        if not is_proteinontology_node(node):
            info('skipping non-PRO node: {}'.format(node['id']))
            continue
        if is_deprecated(node) and not options.include_deprecated:
            info('skipping deprecated: {}'.format(node['id']))
            continue
        process_node(node, graph, options)


def process(fn, options):
    with open(fn) as f:
        data = json.load(f)
    graphs = assure_list(data['graphs'])
    for graph in graphs:
        process_graph(graph, options)


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.files:
        process(fn, args)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
