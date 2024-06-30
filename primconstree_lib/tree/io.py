from ete3 import Tree


def read_trees(input_file: str):
    """Read the tree from the input file in Newick format using the ete3 library and attributes it to Tree class from ete3

    Args:
        input_file (str): Path to the input file.

    Returns:
        Tree: A list of the Trees object
    """
    trees = []
    with open(input_file, "r") as file:
        # Read the tree from the file
        for _, tree in enumerate(file.readlines()):
            tree.strip()
            trees.append(Tree(tree, format=1))
    return trees
