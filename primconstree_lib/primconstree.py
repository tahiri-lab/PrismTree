import networkx as nx
import ete3
from super_graph import SuperGraph
from mst_to_consensus import remove_unecessary_nodes
from parser import read_trees


FILENAME = "datasets/illustration.txt"


inputs = read_trees(FILENAME)
super_graph = SuperGraph(inputs)
super_graph.display_info(True)
super_graph.draw_graph("frequency", True, False)
super_graph.modified_prim(super_graph.root, False)
super_graph.draw_graph("frequency", False, True)

tree = super_graph.to_tree(super_graph.root)
print("Consensus tree with unecessary nodes")
print(tree)
remove_unecessary_nodes(tree, list(super_graph.leaves.values()), True)
print("Final consensus tree")
print(tree)

for n in tree.traverse():
    print(n.name, n.dist)