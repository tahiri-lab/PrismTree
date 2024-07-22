import os
from ete3 import Tree


def read_trees(input_file: str, format=0):
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
            trees.append(Tree(tree, format=format))
    return trees

def phylo_to_ete3(tree):
    newick = tree.format("newick")
    ete_tree = Tree(newick)
    return ete_tree

def create_unique_file(base_filename):
    """
    100% ChatGpt here to be honest
    Take a path, create directories if necessary. If the file already exists, create a new unique filename.
    """
    dir_name = os.path.dirname(base_filename)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    # Check if the file already exists
    if not os.path.exists(base_filename):
        # If the file does not exist, create it
        with open(base_filename, 'w') as file:
            pass
        return base_filename
    
    # If the file exists, append an integer to the filename
    file_extension = ''
    if '.' in base_filename:
        base_name, file_extension = base_filename.rsplit('.', 1)
        base_filename = base_name
        file_extension = '.' + file_extension
    
    counter = 1
    new_filename = f"{base_filename}_{counter}{file_extension}"
    
    while os.path.exists(new_filename):
        counter += 1
        new_filename = f"{base_filename}_{counter}{file_extension}"
    
    # Create the new file with a unique name
    with open(new_filename, 'w') as file:
        pass
    
    return new_filename