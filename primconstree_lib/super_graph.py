import networkx as nx
import matplotlib.pyplot as plt
import ete3
import heapq


def parent_to_graph(parent: list[int], graph: nx.Graph, src: int) -> nx.Graph:
    """
    Create the mst as a nx.Graph instance from the parent list and the original graph
    The transformation keep the edges/nodes features from the original graph
    """
    g = nx.Graph()
    g.add_nodes_from(graph.nodes(data=True))

    for i, p in enumerate(parent):
        if i != src:
            g.add_edge(i, p, avglen=graph[i][p]["avglen"], frequency=graph[i][p]["frequency"])
    
    return g


class SuperGraph:
    def __init__(self, S: list[ete3.Tree]):
        """
        Instanciate and compute a super graph from a list of input trees. 
        Also compute average edge length, node degree and edge frequency, all attached on the nx.Graph instance self.graph
        """
        self.graph : nx.Graph = nx.Graph()
        self.node_ids : dict[frozenset, int] = {}
        self.leaves : dict[str, int] = {}
        self.root : int = None
        self.mst : nx.Graph = None
        self.input : list[ete3.Tree] = S

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

    def get_node_id(self, node: ete3.Tree):
        """
        Get a node id from the tree node (create the id if necessary)
        """
        cluster = frozenset(node.get_leaf_names())
        if cluster not in self.node_ids:
            self.node_ids[cluster] = len(self.node_ids)
        return self.node_ids[cluster]

    def incorporate_tree(self, t: ete3.Tree) -> None:
        """
        Incorporate a tree in the supergraph. Update nodes, edges and metrics
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
        """
        based on https://www.geeksforgeeks.org/prims-algorithm-using-priority_queue-stl/
        Create a maximum spanning tree using an adapted implementation of prim with priority queue
        The following criteria are maximised (from highest to least priority) : edge frequency, node degree (fringe vertex), node degree (MST included vertex)
        arguments:
            src: the source node to start the mst (root in our use case)
            modified: if True, add an additional criteria: the degree of the nodes already included in the mst
        """
        nodes = list(self.graph.nodes.keys())
        n = len(nodes)

        k = (float('inf'), float('inf'), float('inf')) if modified else (float('inf'), float('inf'))
        key = [(float('inf'), float('inf'), float('inf'))] * n 
        parent = [-1] * n    # Keep track of the topology of the mst
        in_mst = [False] * n # To keep track of vertices included in MST

        # Init pq with the source node
        # Tuples will be sorted in lexicographic order
        pq = [] # queue for internal nodes
        crits = (0, 0, 0) if modified else (0, 0)
        heapq.heappush(pq, (*crits, src))
        key[src] = 0

        # Loop until the priority queue becomes empty
        while pq:
            # Extract the id of the next vertex
            u = heapq.heappop(pq)[-1]

            # Abort if u already included
            if in_mst[u]:
                continue

            # Include the vertex in MST
            in_mst[u] = True  

            # Iterate through adjacency list of u
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


        self.mst = parent_to_graph(parent, self.graph, src)
        return self.mst
        
    def to_tree(self, root: int) -> ete3.Tree:
        """
        Return the mst as a ete3.Tree instance.
        arguments:
            root: vertex id coresponding to the root the mst
        """
        tree = ete3.Tree(name=root)
        nodes = {root: tree}
        for u, v in nx.bfs_edges(self.mst, root):
            nodes[v] = nodes[u].add_child(dist=self.mst[u][v]["avglen"], name=v)
        return tree

    def replace_leaves_names(self, t: ete3.Tree):
        """
        Replace leaf ids by leaf names on a Tree
        """
        leaves_names = {v: k for k, v in self.leaves.items()}
        for l in t.get_leaves():
            l.name = leaves_names[l.name]
        return t

    def draw_graph(self, edge_attribute: str = "frequency", display_deg: bool = False, mst: bool = False):
        """
        Draw the nx.Graph instance.
        arguments:
            edge_attribute: which edge attribute to display as edge width
            display_deg: if True, print the list of nodes with their corresponding node degree
            mst: if True, draw self.mst instead of self.graph
        """
        if mst:
            print("\n== Drawing the SuperGraph graph ==\n") 
            G = self.mst
        else:
            print("\n== Drawing the SuperGraph MST ==\n") 
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
        plt.title('Graph with ' + edge_attribute)
        plt.axis('off')
        plt.show()

    def display_info(self, list_nodes: bool = False):
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
