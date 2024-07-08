"""
Module to build the final consensus tree from a MST
"""
import networkx as nx
import ete3
import matplotlib.pyplot as plt
from statistics import fmean


def graph_to_tree(graph : nx.Graph, root, length_attribute: str) -> ete3.Tree:
    """
    create an ete3.Tree object based on a networkx graph
    arguments:
        graph: the graph
        root: vertex coresponding to the root in graph
        length_attribute: the name of the length attribute in the graph
    """
    tree = ete3.Tree(name=root)
    nodes = {root: tree}
    for u, v in nx.bfs_edges(graph, root):
        nodes[v] = nodes[u].add_child(dist=graph[u][v][length_attribute], name=v)
    return tree

def remove_unecessary_nodes(tree: ete3.Tree, leaves: list, average_on_merge: bool) -> None:
    """
    remove unnecessary / redundant internal nodes from a tree
    modify the tree in place
    arguments:
        tree: the tree to clean
        leaves: the name of the leaves (could be the nodes theirselves if we want to change)
        average_on_merge: when deleting a redundant node, if True make average of the merged edges lengths, else sum the lengths
    """
    accumulated_lengths = dict()
    for node in tree.traverse("postorder"): # type: ignore
        if node.name not in leaves:
            children = node.get_children()
            if len(children) == 0:
                node.delete(preserve_branch_length = True)
            elif len(children) == 1:
                c = children[0]
                if c not in accumulated_lengths:
                    accumulated_lengths[c] = [c.dist]
                accumulated_lengths[c].append(node.dist)
                node.delete(preserve_branch_length = True)
    if average_on_merge:
        for node in accumulated_lengths:
            node.dist = fmean(accumulated_lengths[node])

def example():
    """
    Just a sample graph to clean tree process, should be deleted when we are done with it
    """
    # create a sample graph (must be a tree)
    sample = nx.Graph()
    sample.add_node(1)
    sample.add_node(2)
    sample.add_node(3)
    sample.add_node(4)
    sample.add_node(5)
    sample.add_node(6)
    sample.add_node(7)
    sample.add_node(8)
    sample.add_node(9)
    sample.add_edge(1, 2, avglen=1)
    sample.add_edge(2, 3, avglen=3)
    sample.add_edge(1, 4, avglen=5)
    sample.add_edge(1, 5, avglen=6)
    sample.add_edge(5, 6, avglen=1)
    sample.add_edge(6, 7, avglen=3)
    sample.add_edge(6, 8, avglen=2.5)
    sample.add_edge(8, 9, avglen=7)
    LEAVES_NODES = [3, 7, 9]

    #nx.draw(sample)
    #plt.show()

    t = graph_to_tree(sample, 1, "avglen")
    print(t)
    print(t.write(format=3))
    remove_unecessary_nodes(t, LEAVES_NODES, True)
    print(t)
    print(t.write(format=3))