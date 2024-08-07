""" Module in charge of generating the consensus tree using the PrimConsTree algorithm
"""
import logging
from statistics import fmean
import ete3
from .super_graph import SuperGraph


def remove_unecessary_nodes(tree: ete3.Tree, leaves: list[str],
                            average_on_merge: bool = False) -> None:
    """ Remove unnecessary / redundant internal nodes from a tree. 
        Modify the tree in place.

    Args:
        tree (ete3.Tree): the tree to clean
        leaves (list[str]): the name of the original leaves
        average_on_merge (bool, optional): If True, average edge length when 
            removing redundant node, else sum. Defaults to False.
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
        for node, lengths in accumulated_lengths.items():
            node.dist = fmean(lengths)


def primconstree(inputs: list[ete3.Tree], old_prim: bool = False, avg_on_merge: bool = False,
                 debug: bool = False) -> ete3.Tree:
    """ Generate the consensus tree from a set of phylogenetic trees
        using the PrimConsTree algorithm

    Args:
        inputs (list[ete3.Tree]): list of input trees
        old_prim (bool, optional): if True, use previous mst criteria (min branch length and edge frequency) for modified_prim. Defaults to False.
        avg_on_merge (bool, optional): if True, use argument average_on_merge for remove_unecessary_nodes(). Defaults to False.
        debug (bool, optional): If True, display the super-graph / consensus tree at several steps. Defaults to False.

    Returns:
        ete3.Tree: the consensus tree
    """
    logging.debug("Generating PrimConsTree")

    # Super graph generation
    super_graph = SuperGraph(inputs)
    logging.debug("Super-Graph Generated")
    if debug:
        super_graph.display_info(False)
        super_graph.draw_graph("frequency", False, False)

    # Modified Prim algorithm
    super_graph.modified_prim(super_graph.root, old_prim)
    logging.debug("MST found with usig %s criteria", "previous" if old_prim else "current")
    if debug:
        super_graph.draw_graph("avglen", False, True)

    # Conversion to ete3
    tree = super_graph.to_tree(super_graph.root)
    if debug:
        print("\nConsensus tree with unecessary nodes\n")
        print(tree)

    # Cleaning the tree from unnecessary nodes
    remove_unecessary_nodes(tree, list(super_graph.leaves.values()), avg_on_merge)
    tree = super_graph.replace_leaves_names(tree)
    logging.debug("Proper consensus tree generated from MST (avg_on_merge = %s)", str(avg_on_merge))
    if debug:
        print("\nFinal consensus tree:\n")
        print(tree)

    if debug:
        print("\nNodes distances to parent:")
        for n in tree.traverse():
            print("\t", n.name, "=>", n.dist)

    return tree
    