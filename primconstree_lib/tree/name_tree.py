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


class TreeStructure:
    def __init__(self, tree: Tree):
        self.tree = tree
        self.leaf_nodes = self.identify_nodes()
        self.internal_nodes = self.update_internal_node_names()

    def identify_nodes(self) -> list:
        """Identify leaf nodes in the tree.

        Returns:
            list: List of leaf nodes in the tree.
        """
        leaf_nodes = []
        # Use ete3 Tree.traverse() method to traverse the tree in postorder: children before parents
        for node in self.tree.traverse("postorder"):  # type: ignore
            if node.is_leaf():
                leaf_nodes.append(node.name)
        return leaf_nodes

    def update_internal_node_names(self) -> list:
        """Update the internal node names in the tree by concatenating the names of their children.

        Returns:
            list: List of internal nodes in the tree.
        """
        internal_nodes = []

        def generate_unique_name(name: str) -> str:
            """Generate a unique name for an internal node by adding a suffix.

            Args:
                name (str): The name of the internal node.

            Returns:
                str: The unique name of the internal node with a suffix.
            """
            suffix = 1
            while name + str(suffix) in self.leaf_nodes:
                suffix += 1
            return name + str(suffix)

        def update_internal_node(node):
            """Update the name of an internal node by concatenating the names of its children.

            Args:
                node (TreeNode): The internal node to update.
            """
            if not node.is_leaf():
                children_names = sorted([child.name for child in node.children])
                new_name = "".join(children_names)
                if new_name in self.leaf_nodes:
                    new_name = generate_unique_name(new_name)
                node.name = new_name
                internal_nodes.append(node.name)

        for node in self.tree.traverse("postorder"):  # type: ignore
            update_internal_node(node)

        return internal_nodes


# Test the TreeStructure class:
input_file = (
    r"C:\Users\harsh\s\PrimConsTree\PrimConsTree\datasets\simulated\Trex_trees20.txt"
)


input_tree = read_tree(input_file)
tree_structure = TreeStructure(input_tree)
print(tree_structure.leaf_nodes)
print(tree_structure.internal_nodes)
print(input_tree)
