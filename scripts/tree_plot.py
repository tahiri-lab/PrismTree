import matplotlib.pyplot as plt
from Bio import Phylo

NEWICK = "outputs/kmedoids_modified_noavg/cluster5_consensus.txt"
SAVEPLOT = "outputs/kmedoids_modified_noavg/cluster5_consensus.png"

# Read the Newick tree from a file
tree = Phylo.read(NEWICK, "newick")

# Plot the tree
fig = plt.figure(figsize=(10, 5))  # Set the size of the plot
axes = fig.add_subplot(1, 1, 1)
Phylo.draw(tree, do_show=False, axes=axes)

# Save the plot to a file
plt.savefig(SAVEPLOT)

# Display the plot
plt.show()