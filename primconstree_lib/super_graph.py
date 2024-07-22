""" Handle operations related to the super-graph in primconstree such as:
- construction from set of trees
- finding mst
"""
import heapq
import networkx as nx
import matplotlib.pyplot as plt
import ete3


def parent_to_graph(parent: list[int], graph: nx.Graph, src: int) -> nx.Graph:
    """ Yield a spanning tree as a nx.Graph instance
        from a list of parents and a graph instance

    Args:
        parent (list[int]): list of parent node id for each node in graph
        graph (nx.Graph): the graph instance to build the mst from
        src (int): the source node id to start the mst

    Returns:
        nx.Graph: the mst as a graph instance
    """
    g = nx.Graph()
    g.add_nodes_from(graph.nodes(data=True))

    for i, p in enumerate(parent):
        if i != src:
            g.add_edge(i, p, avglen=graph[i][p]["avglen"], frequency=graph[i][p]["frequency"])

    return g


class SuperGraph:
    """
    A class to store and use the supergraph. Main purposes are:
    - create the graph from a set of trees on the same taxa
    - compute a maximum spanning tree based on edge frequency and node degree
    - display informations from the super graph or its corresponding maximum spanning tree
    - yield the maximum spanning tree as an ete3.Tree instance
    """
    def __init__(self, inputs: list[ete3.Tree]):
        """ Instanciate the super-graph and compute associated metrics

        Args:
            inputs (list[ete3.Tree]): the list of trees to build the super-graph from
        """
        # A graph instance to hold : connectivity, node degree, average edge length, edge frequency
        self.graph : nx.Graph = nx.Graph()
        # Mapping of node ids following this pattern : set of leaf names (frozenset) => id (integer)
        self.node_ids : dict[frozenset, int] = {}
        # Mapping of the leaves to store which node should stay a leaf
        self.leaves : dict[str, int] = {}
        # Node id corresponding to the root node
        self.root : int = None
        # A graph instance to store the mst (keep other attributes from self.graph)
        self.mst : nx.Graph = None
        # The list of input trees (just in case)
        self.input : list[ete3.Tree] = inputs

        if not S:
            raise ValueError("Need at least one tree to build the SuperGraph")

        # Parse and leaves and map leaves ids
        for i, l in enumerate(S[0].get_leaf_names()):
            self.node_ids[frozenset({l})] = i
            self.leaves[l] = i
            self.graph.add_node(i, ndegree=0)

        # Identify root node
        self.root = len(self.node_ids)
        self.node_ids[frozenset(self.leaves.keys())] = self.root
        self.graph.add_node(self.root, ndegree=0)

        # Build the SuperGraph
        for t in self.input:
            self.incorporate_tree(t)

        # Update average branch length
        for u, v in self.graph.edges():
            self.graph[u][v]["avglen"] = self.graph[u][v]["avglen"] / self.graph[u][v]["frequency"]

    def get_node_id(self, node: ete3.Tree) -> int:
        """ Return a node id (int) from a ete3 node instance (create if not exist)
            Id is created from the set of leaf names in the subtree

        Args:
            node (ete3.Tree): the node to get the id from

        Returns:
            int: the node id
        """
        cluster = frozenset(node.get_leaf_names())
        if cluster not in self.node_ids:
            self.node_ids[cluster] = len(self.node_ids)
        return self.node_ids[cluster]

    def incorporate_tree(self, t: ete3.Tree) -> None:
        """ Incorporate a tree in the supergraph. 
            Update nodes, edges and node degree, edge frequency, average edge length

        Args:
            t (ete3.Tree): the tree to incorporate
        """
        # Preorder ensure to incorporate parent before children
        for node in t.traverse("preorder"):
            nid = self.get_node_id(node)

            # The node is not in the graph
            if nid not in self.graph.nodes:
                self.graph.add_node(nid, ndegree=0)

            # The node is not the root
            if node.up:
                self.graph.nodes[nid]["ndegree"] += 1
                parent = self.get_node_id(node.up)

                # The edge is not in the graph
                if parent not in self.graph[nid]:
                    self.graph.add_edge(parent, nid, avglen=0, frequency=0)

                self.graph[parent][nid]["avglen"] += node.dist
                self.graph[parent][nid]["frequency"] += 1

    def modified_prim(self, src: int, modified: bool) -> nx.Graph:
        """ Create a maximum spanning tree using a priority queue.
            MST is based on (in this order) :
            - edge frequency, 
            - node degree (fringe vertex), 
            - node degree (MST included vertex)
            (see https://www.geeksforgeeks.org/prims-algorithm-using-priority_queue-stl/)

        Args:
            src (int): the source node id to start the mst
            modified (bool): if True use the last criterion (degree of included vertex)
        
        Returns:
            nx.Graph: the mst as a graph instance
        """
        nodes = list(self.graph.nodes.keys())
        n = len(nodes)

        k = (float('inf'), float('inf'), float('inf')) if modified else (float('inf'), float('inf'))
        key = [k] * n
        parent = [-1] * n    # Keep track of the topology of the mst
        in_mst = [False] * n # To keep track of vertices included in MST

        # Init the queue with the source node
        pq = []
        crits = (0, 0, 0) if modified else (0, 0)
        heapq.heappush(pq, (*crits, src))
        key[src] = 0

        # Loop until the priority queue becomes empty
        while pq:
            u = heapq.heappop(pq)[-1]
            if in_mst[u]:
                continue

            in_mst[u] = True

            for v in self.graph[u]:
                if v in self.leaves.values():
                    continue
                ndeg_out = 1/self.graph.nodes[v]["ndegree"] if self.graph.nodes[v]["ndegree"] > 0 else float('inf')
                ndeg_in = 1/self.graph.nodes[u]["ndegree"] if self.graph.nodes[u]["ndegree"] > 0 else float('inf')
                freq = 1/self.graph[u][v]["frequency"] if self.graph[u][v]["frequency"] > 0 else float('inf')
                weights = (freq, ndeg_out, ndeg_in) if modified else (freq, ndeg_out)
                if not in_mst[v] and key[v] > weights:
                    key[v] = weights
                    heapq.heappush(pq, (*key[v], v))
                    parent[v] = u

        # Attach the leaf nodes
        for u in self.leaves.values():
            for v in self.graph[u]:
                ndeg_in = 1/self.graph.nodes[v]["ndegree"] if self.graph.nodes[v]["ndegree"] > 0 else float('inf')
                freq = 1/self.graph[u][v]["frequency"] if self.graph[u][v]["frequency"] > 0 else float('inf')
                weights = (freq, ndeg_in, 0) if modified else (freq, ndeg_in)
                if key[u] > weights:
                    key[u] = weights
                    parent[u] = v

        # Build the networkx instance from a list of parents
        self.mst = parent_to_graph(parent, self.graph, src)
        return self.mst

    def to_tree(self, root: int) -> ete3.Tree:
        """ Return the maximum spanning tree as an ete3.Tree instance from the nx.Graph

        Args:
            root (int): the root node id of the tree

        Returns:
            ete3.Tree: the mst as a tree instance
        """
        tree = ete3.Tree(name=root)
        nodes = {root: tree}
        for u, v in nx.bfs_edges(self.mst, root):
            nodes[v] = nodes[u].add_child(dist=self.mst[u][v]["avglen"], name=v)
        return tree

    def replace_leaves_names(self, t: ete3.Tree) -> ete3.Tree:
        """ Replace leaf node ids in the tree by their original leaf names

        Args:
            t (ete3.Tree): the tree to replace the leaf names

        Returns:
            ete3.Tree: the tree with leaf names instead of ids
        """
        leaves_names = {v: k for k, v in self.leaves.items()}
        for l in t.get_leaves():
            l.name = leaves_names[l.name]
        return t

    def draw_graph(self, edge_attribute: str = "frequency", display_deg: bool = False,
                   mst: bool = False) -> None:
        """ Draw the supergraph or the mst with networkx and matplotlib

        Args:
            edge_attribute (str, optional): The attribute to display as edge label. Defaults to "frequency".
            display_deg (bool, optional): If True, display node degrees in the console. Defaults to False.
            mst (bool, optional): If True, draw the mst, otherwise the super-graph. Defaults to False.
        """
        if mst:
            name = "MST "
            G = self.mst
        else:
            name = "Super-Graph "
            G = self.graph

        if display_deg:
            print("Nodes degrees:")
            for node, data in G.nodes(data=True):
                print(f"\t Node {node}: ndegree = {data['ndegree']}")
            
        # Draw the graph with edge frequency reflected in edge width
        edge_widths = [data[edge_attribute] for u, v, data in G.edges(data=True)]
        pos = nx.spring_layout(G)  # Layout for the graph

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500)

        # Draw edges with edge width based on frequency attribute
        nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='gray')

        # Draw edge labels (optional)
        edge_labels = {(u, v): data[edge_attribute] for u, v, data in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        # Draw node labels
        nx.draw_networkx_labels(G, pos, font_weight='bold')

        # Display the graph
        plt.title(name + 'with ' + edge_attribute)
        plt.axis('off')
        plt.show()

    def display_info(self, list_nodes: bool = False) -> None:
        """
        Display object usefull information.
        arguments:
            list_nodes: if True, list all distinct nodes with their corresponding ids
        """
        print("\n== Displaying SuperGraph infos ==\n")
        print("Number of input trees :", len(self.input))
        print("Number of distict nodes identified :", len(self.node_ids))
        print("Species mapping :")
        for l, i in self.leaves.items():
            print("\t", i, "<=>", l)

        print("Root node id: ", self.root)

        if list_nodes:
            print("Listing all distinct node identifier :")
            for n, i in self.node_ids.items():
                print("\t", i, "<=>", n)
