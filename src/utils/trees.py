""" Utilities to manipulate trees
"""
import ete3
from Bio import Phylo

def read_trees(input_file: str, nwk_format: int = 0) -> list[ete3.Tree]:
    """ Read the trees from the input file in Newick format using ete3

    Args:
        input_file (str): Path to the input file.
        nwk_format (int, optional): The format of the Newick tree (see ete3 references tutorial). Defaults to 0.

    Returns:
        list[ete3.Tree]: list of the Trees object
    """
    trees = []
    with open(input_file, "r") as file:
        # Read the tree from the file
        for _, tree in enumerate(file.readlines()):
            tree.strip()
            trees.append(ete3.Tree(tree, format=nwk_format))
    return trees

def phylo_to_ete3(tree: Phylo.BaseTree.Tree) -> ete3.Tree:
    """ Convert a Biopython tree to an ete3 tree

    Args:
        tree (Phylo.BaseTree.Tree): the Biopython tree to convert

    Returns:
        ete3.Tree: the ete3 tree
    """
    newick = tree.format("newick")
    ete_tree = ete3.Tree(newick)
    return ete_tree