import os
import sys


# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to the system path
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from tree.class_tree import Tree
from tree.io import read_trees


def rename_set_of_trees(input_file):
    """Give unique names to each node in a set of trees by a hash function to integers mapping.

    Args:
        input_file (str): The path to the input file containing the trees.
    """
    trees = read_trees(input_file)
    trees_list = []
    for tree_data in trees:
        tree = Tree(tree_data)
        trees_list.append(tree)

    edge_hash_map = {}
    hash_counter = 0
    # For all  trees, check if the edge is already mapped to an integer, if not, map it to a new integer:
    for tree in trees_list[0:]:
        for edge in tree.edges_list:
            edge_set = frozenset({edge[0], edge[1]})
            if edge_set not in edge_hash_map:
                edge_hash_map[edge_set] = hash_counter
                hash_counter += 1
            # print(edge_set, "mapped to", edge_hash_map[edge_set])

    return trees_list, edge_hash_map


rename_set_of_trees(
    r"C:\Users\harsh\s\PrimConsTree\datasets\simulated\trex_treestest.txt"
)
