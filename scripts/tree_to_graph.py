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
from primconstree_lib.graph.construct_graph import add_vertex, add_edge


def main(input_file):
    input_tree = read_tree(input_file)
    tree_structure = TreeStructure(input_tree)
    print(tree_structure.leaf_nodes)
    print(tree_structure.internal_nodes)
    print(input_tree)
    print(tree_structure.unique_nodes)
    print(tree_structure.distances)
    for node in tree_structure.node_names:
        add_vertex(node)
    # add edge
    for i in range(0, tree_structure.num_nodes):
        for j in range(i + 1, len(tree_structure.node_names)):
            v1 = tree_structure.node_names[i]
            v2 = tree_structure.node_names[j]
            # to be continued: add the distance between two nodes
            # if check_direct_connection(tree, v1, v2):
            #     distance = round(distances.get((v1, v2), 0), 2)
            # print("\n\nTree nodes conection : ",v1,"-",v2,"-",distance,"\n")
            add_edge(v1, v2, 1)  # , distance)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a graph from a tree file.")
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the input tree file",
    )

    args = parser.parse_args()

    main(args.input_file)
