from ete3 import Tree


class TreeStructure:
    def __init__(self, tree: Tree):
        self.tree = tree
        self.leaf_nodes = self.identify_nodes()
        self.unique_nodes = self.unique_nodes_in_tree()
        self.internal_nodes = self.update_internal_node_names()
        self.distances = self.get_distances_and_name()[0]
        self.node_names = self.get_distances_and_name()[1]
        self.num_nodes = len(self.unique_nodes)

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

    def unique_nodes_in_tree(self):
        """Identify unique nodes in the tree with memory address.

        Returns:
            list: List of unique nodes in the tree with memory address.
        """

        unique_nodes = set(self.tree.iter_leaves())
        unique_nodes.update(self.tree.traverse("postorder"))  # type: ignore
        return unique_nodes

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

    def get_distances_and_name(self):
        """Get the distances between the nodes in the tree.

        Returns:
            dict: A dictionary containing the distances between the nodes in the tree.
        """
        # Create a matrix to represent the distances
        node_names = [node.name for node in self.unique_nodes]
        node_names.sort(key=lambda x: (self.tree & x).get_distance(self.tree))

        distances = {}
        all_nodes = list(self.tree.traverse())  # type: ignore # Collect all nodes
        for i in range(len(all_nodes)):
            for j in range(i + 1, len(all_nodes)):
                node1 = all_nodes[i]
                node2 = all_nodes[j]
                distance = node1.get_distance(
                    node2
                )  # Calculate distance using the tree library function
                distance = round(distance, 2)
                distances[(node1.name, node2.name)] = distance
                distances[(node2.name, node1.name)] = distance

        return distances, node_names
