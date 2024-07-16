import networkx as nx
import ete3
import matplotlib.pyplot as plt
from statistics import fmean


def remove_unecessary_nodes(tree: ete3.Tree, leaves: list, average_on_merge: bool = True) -> None:
    """
    remove unnecessary / redundant internal nodes from a tree
    modify the tree in place
    arguments:
        tree: the tree to clean
        leaves: the name of the leaves (could be the nodes theirselves if we want to change)
        average_on_merge: when deleting a redundant node, if True make average of the merged edges lengths, else sum the lengths
    """
    accumulated_lengths = dict()
    for node in tree.traverse("postorder"):
        if node.name not in leaves:
            children = node.get_children()
            if len(children) == 0:
                node.delete(prevent_nondicotomic = False, preserve_branch_length = True)
            elif len(children) == 1:
                c = children[0]
                if c not in accumulated_lengths:
                    accumulated_lengths[c] = [c.dist]
                accumulated_lengths[c].append(node.dist)
                node.delete(prevent_nondicotomic = False, preserve_branch_length = True)
    if average_on_merge:
        for node in accumulated_lengths:
            node.dist = fmean(accumulated_lengths[node])
