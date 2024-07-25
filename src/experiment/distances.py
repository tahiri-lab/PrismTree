""" Implementation of metrics to compare trees
"""
from math import sqrt


def average_rf(input_trees, consensus):
    rf_sum = 0
    for tree in input_trees:
        rf, max_rf = tree.robinson_foulds(consensus, unrooted_trees=True)[:2]
        rf_sum += rf / max_rf
    return rf_sum / len(input_trees)


def bsd(t1, t2, normalize=True):
    # Get distance of each bipartition in each tree
    dist_t1 = {}
    for node in t1.traverse():
        if node.up:
            clade = frozenset(node.get_leaf_names())
            dist_t1[clade] = node.dist
    size_t1 = sum(dist_t1.values()) if normalize else 1

    dist_t2 = {}
    for node in t2.traverse():
        if node.up:
            clade = frozenset(node.get_leaf_names())
            dist_t2[clade] = node.dist
    size_t2 = sum(dist_t2.values()) if normalize else 1

    # Fill the bipartition missing in one tree with 0
    for n in dist_t1:
        if n not in dist_t2:
            dist_t2[n] = 0
    for n in dist_t2:
        if n not in dist_t1:
            dist_t1[n] = 0

    # Compute the distance
    diffs = [((dist_t1[n] / size_t1) - (dist_t2[n] / size_t2))**2 for n in dist_t1]
    return sqrt(sum(diffs))


def average_bsd(input_trees, consensus, normalize=True):
    total = 0
    for tree in input_trees:
        total += bsd(tree, consensus, normalize)
    return total / len(input_trees)
