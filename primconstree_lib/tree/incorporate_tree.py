import ete3
import os
import sys

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to the system path
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from tree.io import read_trees


def incorporate_tree(tree):
    nodes_list = []
    in_degree = {}
    edges_list = []
    weights_list = []

    unnamed_node_counter = 0

    for node in tree.traverse():
        # Name internal nodes:
        if not node.name:
            node.name = chr(unnamed_node_counter + 65)
            unnamed_node_counter += 1

        # Add node to the list of nodes:
        if node.name not in nodes_list:
            nodes_list.append(node.name)
            in_degree[node.name] = 0

        # Add parent node to the list of nodes and update in-degree:
        if node.up is not None:
            parent_name = node.up.name
            in_degree[node.name] += 1
            edge = (parent_name, node.name)
            # Add edge to the list of edges:
            if edge not in edges_list:
                edges_list.append(edge)
                weights_list.append(node.dist)

    print("Nodes list:", nodes_list)
    print("In-degree dictionary:", in_degree)
    print("Edges list:", edges_list)
    print("Weights list:", weights_list)


# def incorporate_tree(tree):
#     for node in tree.traverse():
#         if node not in  G:
#             add node in G
#         if node.up is not None: # the node is not the root
#             if node.up not in G:
#                 add node.up in G

#             in degree of node += 1

#             edge = (node.up, node) # depend on edges representation

#             if edge not in G:
#                 # incorporate edge in the graph
#                 add edge in G
#                 frequency of edge = 1
#                 average length of edge = length of edge
#             else:
#                 # update frequency and average length
#                 frequency of edge += 1
#                 # use average edge length as cumulative edge length untill the end
#                 average length of edge += length of edge
trees = read_trees(
    r"C:\Users\harsh\s\PrimConsTree\datasets\simulated\trex_treestest.txt"
)

for i in range(len(trees)):
    incorporate_tree(trees[i])
    print(trees[i])
