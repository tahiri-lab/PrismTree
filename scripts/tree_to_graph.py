import sys
import os
import argparse

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to the system path
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from primconstree_lib.tree.io import read_tree
from primconstree_lib.tree.name_tree import TreeStructure


def main(input_file):
    input_tree = read_tree(input_file)
    tree_structure = TreeStructure(input_tree)
    print(tree_structure.leaf_nodes)
    print(tree_structure.internal_nodes)
    print(input_tree)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process a tree file and display its structure."
    )
    parser.add_argument("input_file", type=str, help="Path to the input tree file")

    args = parser.parse_args()

    main(args.input_file)
