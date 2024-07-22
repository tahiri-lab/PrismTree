""" Implementation of metrics to compare trees
"""


def average_rf(input_trees, consensus):
    rf_sum = 0
    for tree in input_trees:
        rf, max_rf = tree.robinson_foulds(consensus, unrooted_trees=True)[:2]
        rf_sum += rf / max_rf
    return rf_sum / len(input_trees)
