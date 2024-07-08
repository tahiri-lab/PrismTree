import os
import sys


# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to the system path
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from tree.class_tree import Tree
from tree.io import read_trees


def compute_avg_bl_and_edge_freq(input_file):
    """Give unique names to each node in a set of trees by a hash function to integers mapping.

    Args:
        input_file (str): The path to the input file containing the trees.

    Returns:
        tuple: A tuple containing the list of trees, the hash map of edges to integers, and the average branch length of each edge in the given set of trees.
    """
    trees = read_trees(input_file)
    trees_list = []
    for tree_data in trees:
        tree = Tree(tree_data)
        trees_list.append(tree)

    edge_hash_map_node = {}
    edge_hash_map_edge = {}
    hash_counter_node = 0
    hash_counter_edge = 0
    branch_count = {}
    total_branch_length = {}
    edge_frequency = {}
    # For all trees, check if node is already mapped to an integer, if not, map it to a new integer:
    for tree in trees_list:
        for node in tree.nodes_list:
            if node not in edge_hash_map_node:
                edge_hash_map_node[node] = hash_counter_node
                hash_counter_node += 1
    # For all trees, check if the edge is already mapped to an integer, if not, map it to a new integer:
    for tree in trees_list:

        for edge in tree.edges_list:
            edge_set = frozenset({edge[0], edge[1]})
            if edge_set not in edge_hash_map_edge:
                edge_hash_map_edge[edge_set] = hash_counter_edge
                branch_count[hash_counter_edge] = 1
                edge_frequency[hash_counter_edge] = 1
                total_branch_length[hash_counter_edge] = tree.weights_list[
                    tree.edges_list.index(edge)
                ]
                hash_counter_edge += 1
            else:
                edge_hash = edge_hash_map_edge[edge_set]
                branch_count[edge_hash] += 1
                total_branch_length[edge_hash] += tree.weights_list[
                    tree.edges_list.index(edge)
                ]
                edge_frequency[edge_hash] += 1

    average_branch_length = {
        key: total_branch_length[key] / branch_count[key] for key in total_branch_length
    }

    return (
        trees_list,
        edge_hash_map_node,
        edge_hash_map_edge,
        average_branch_length,
        edge_frequency,
    )


print(
    compute_avg_bl_and_edge_freq(
        r"C:\Users\harsh\s\PrimConsTree\datasets\simulated\trex_treestest.txt"
    )
)
