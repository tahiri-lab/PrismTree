from ete3 import Tree


def read_tree(input_file: str) -> Tree:
    """Read the tree from the input file in Newick format using the ete3 library.

    Args:
        input_file (str): Path to the input file.

    Returns:
        Tree: The tree object.
    """
    with open(input_file, "r") as file:
        # Read the tree from the file
        tree = Tree(file.readline().strip(), format=1)
    return tree
