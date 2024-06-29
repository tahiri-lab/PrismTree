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

    # in_degree dict:
    # key: node_name, value: in_degree of the given node
    in_degree = {}
    edges_list = []
    weights_list = []
    #
    # Adds node in tree from closest node to root to farthest:
    for node in tree.traverse():
        if not None:
            if node not in nodes_list:
                nodes_list.append(node)
                # if node.up is not None:
                #     if node.up not in nodes_list:
                #         node_up = node.up
                #         nodes_list.append(node_up)

            in_degree.update({node: 0})
            in_degree[node] += 1
    # print(nodes_list)

    print(in_degree)


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
print(trees)
for i in range(len(trees)):
    incorporate_tree(trees[i])
