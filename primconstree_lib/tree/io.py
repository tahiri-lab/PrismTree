from ete3 import Tree


def read_trees(input_file: str):
    """Read the tree from the input file in Newick format using the ete3 library.

    Args:
        input_file (str): Path to the input file.

    Returns:
        Tree: The tree object.
    """
    trees = []
    with open(input_file, "r") as file:

        # Read the tree from the file
        for line, tree in enumerate(file.readlines()):
            tree.strip()
            trees.append(Tree(tree, format=1))
    return trees


# treess = read_trees(
#     r"C:\Users\harsh\s\PrimConsTree\datasets\simulated\trex_treestest.txt"
# )
# for tree in treess:
#     print(tree)
