import sys
import os
import argparse

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to the system path
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from primconstree_lib.tree.io import read_trees
from primconstree_lib.tree.name_tree import TreeStructure


def main(input_file):
    input_tree = read_trees(input_file)
    for tree in input_tree:

        tree_structure = TreeStructure(tree)
        print(tree_structure.leaf_nodes)
        print(tree_structure.internal_nodes)
        print(input_tree)
        print(tree_structure.unique_nodes)
        print(tree_structure.distances)

    # Show graph
    # Modified Prim's algorithm
    # Optimal path from root to leaf
    # Consensus trees comparison for modified Prim's algorithm and Optimal path from root to leaf


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a graph from a tree file.")
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the input tree file",
    )

    args = parser.parse_args()

    main(args.input_file)
