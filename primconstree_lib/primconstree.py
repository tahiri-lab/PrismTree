import networkx as nx
import ete3
from super_graph import SuperGraph
from mst_to_consensus import remove_unecessary_nodes
from parser import read_trees
from output import create_unique_file


INPUT = "datasets/illustrations/fig5.txt"
OUTPUT = "outputs/illustrations/fig5_consensus.txt"

MODIFIED_PRIM = True # if true, additionaly consider node degree of already included nodes
AVERAGE_BRANCH_LENGTH = True # if true average lenght when deleting unnecessary internal nodes, else just sum up edge lengths


inputs = read_trees(INPUT)
super_graph = SuperGraph(inputs)
super_graph.display_info(True)
super_graph.draw_graph("frequency", True, False)
super_graph.modified_prim(super_graph.root, MODIFIED_PRIM)
super_graph.draw_graph("avglen", False, True)

tree = super_graph.to_tree(super_graph.root)
print("\nConsensus tree with unecessary nodes\n")
print(tree)

remove_unecessary_nodes(tree, list(super_graph.leaves.values()), AVERAGE_BRANCH_LENGTH)
tree = super_graph.replace_leaves_names(tree)
print("\nFinal consensus tree\n")
print(tree)

print("\nNodes distances to parent:")
for n in tree.traverse():
    print("\t", n.name, "=>", n.dist)

print("\nSaving consensus tree to output file", OUTPUT)
filename = create_unique_file(OUTPUT)
if filename != OUTPUT:
    print("WARNING : File", OUTPUT, "already exists, saving to", filename, "instead")
tree.write(outfile=filename, format=1)
print("Consensus tree saved to output file", OUTPUT)