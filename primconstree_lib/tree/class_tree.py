import os
import sys

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to the system path
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# from tree.io import read_trees


class Tree:
    """
    From a tree (newick format), return a list of nodes, in-degree of each node, a list of edges, and a list of weights.

    """

    def __init__(self, tree):
        self.nodes_list, self.in_degree, self.edges_list, self.weights_list = (
            self.incorporate_tree(tree)
        )
        self.edge_names = []

    def traverse(self, order="preorder"):
        # Dummy implementation of traverse. Replace with actual tree traversal logic.
        return []

    def incorporate_tree(self, tree):
        nodes_list = []
        in_degree = {}
        edges_list = []
        weights_list = []

        node_counter = 0
        # Rename internal nodes in reverse order:
        for node in tree.traverse("postorder"):
            # Map node name to a unique name by using the name of the node plus the counter:
            if not node.name:
                node.name = node.children[0].name + node.children[1].name
            node_counter += 1

        for node in tree.traverse():
            # Map all nodes to a unique name:

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

        # print("Nodes list:", nodes_list)
        # print("In-degree dictionary:", in_degree)
        # print("Edges list:", edges_list)
        # print("Weights list:", weights_list)

        return nodes_list, in_degree, edges_list, weights_list


# trees = read_trees(
#     r"C:\Users\harsh\s\PrimConsTree\datasets\simulated\trex_treestest.txt"
# )
# for tree in trees:
#     t = Tree(tree)
#     t.incorporate_tree(tree)
