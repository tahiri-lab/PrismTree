import os
import sys


# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to the system path
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from tree.class_tree import Tree
from tree.io import read_trees


def rename_set_of_trees_compute_avg_branch_length(input_file):
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
    branch_count = {}
    total_branch_length = {}

    # For all trees, check if the edge is already mapped to an integer, if not, map it to a new integer:
    for tree in trees_list:
        for edge in tree.edges_list:
            edge_set = frozenset({edge[0], edge[1]})
            if edge_set not in edge_hash_map:
                edge_hash_map[edge_set] = hash_counter
                branch_count[hash_counter] = 1
                total_branch_length[hash_counter] = tree.weights_list[
                    tree.edges_list.index(edge)
                ]
                hash_counter += 1
            else:
                edge_hash = edge_hash_map[edge_set]
                branch_count[edge_hash] += 1
                total_branch_length[edge_hash] += tree.weights_list[
                    tree.edges_list.index(edge)
                ]

    average_branch_length = {
        key: total_branch_length[key] / branch_count[key] for key in total_branch_length
    }

    return trees_list, edge_hash_map, average_branch_length


print(
    rename_set_of_trees_compute_avg_branch_length(
        r"C:\Users\harsh\s\PrimConsTree\datasets\simulated\trex_treestest.txt"
    )
)
