# def incorporate_tree(tree):
#     for node in tree.traverse():
#         if node not in G:
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

# def build_graph():
#     G = empty graph
#     # build the graph
#     for tree in input trees:
#         rename tree internal nodes
#         incorporate_tree(tree)
#     # update average edge length
#     for edge in G:
#         average length of edge = average length of edge / frquency of edge
