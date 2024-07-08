import networkx as nx
import heapq

FREQUENCY_W = "frequency"
N_DEGREE = "ndegree"
AVG_LEN = "avglen"


def parent_to_mst(parent: list[int], graph: nx.Graph, src: int) -> nx.Graph:
    """
    Create the mst as a nx.Graph instance from the parent list and the original graph
    The transformation keep the edges/nodes features from the original graph
    """
    mst = nx.Graph()
    mst.add_nodes_from(graph.nodes(data=True))

    for i, p in enumerate(parent):
        if i != src:
            mst.add_edge(
                i, p, avglen=graph[i][p][AVG_LEN], frequency=graph[i][p][FREQUENCY_W]
            )

    return mst


# based on https://www.geeksforgeeks.org/prims-algorithm-using-priority_queue-stl/
def modified_prim(graph: nx.Graph, src: int, leaves: list[int]) -> list[int]:
    """
    Create a maximum spanning tree using an adapted implementation of prim with priority queue
    The following criteria are maximised (from highest to least priority) : edge frequency, node degree (fringe vertex)
    arguments:
        graph: a networkx connected graph, nodes must be labelled by integer from 0 to len(graph.nodes) - 1, edge frequency and node degree values must be attached
        src: the source node to start the mst (root in our use case)
        leaves: a list of vertex supposed to be leaves : those are attached after the others
    return:
        parent: a list of integer that hold the parent node of each node in the mst (source parent is -1)
    """
    nodes = list(graph.nodes.keys())
    n = len(nodes)

    key = [(float("inf"), float("inf"))] * n
    parent = [-1] * n  # Keep track of the topology of the mst
    in_mst = [False] * n  # To keep track of vertices included in MST

    # Init pq with the source node
    # Tuples will be sorted in lexicographic order
    pq = []  # queue for internal nodes
    heapq.heappush(pq, (0, 0, src))
    key[src] = 0 # type: ignore

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
        for v in graph[u]:
            if v in leaves:
                continue
            ndeg_out = (
                1 / graph.nodes[v][N_DEGREE]
                if graph.nodes[v][N_DEGREE] > 0
                else float("inf")
            )
            freq = (
                1 / graph[u][v][FREQUENCY_W]
                if graph[u][v][FREQUENCY_W] > 0
                else float("inf")
            )
            weights = (freq, ndeg_out)
            if not in_mst[v] and key[v] > weights:
                key[v] = weights
                heapq.heappush(pq, (key[v][0], key[v][1], v))
                parent[v] = u

    # Attach the leaf nodes
    for u in leaves:
        for v in graph[u]:
            ndeg_in = (
                1 / graph.nodes[u][N_DEGREE]
                if graph.nodes[u][N_DEGREE] > 0
                else float("inf")
            )
            freq = (
                1 / graph[u][v][FREQUENCY_W]
                if graph[u][v][FREQUENCY_W] > 0
                else float("inf")
            )
            weights = (freq, ndeg_in, 0)
            if key[u] > weights:
                key[u] = weights # type: ignore
                parent[u] = v

    return parent_to_mst(parent, graph, src)  # type: ignore


# based on https://www.geeksforgeeks.org/prims-algorithm-using-priority_queue-stl/
def modified_modified_prim(graph: nx.Graph, src: int, leaves: list[int]) -> list[int]:
    """
    Create a maximum spanning tree using an adapted implementation of prim with priority queue
    The following criteria are maximised (from highest to least priority) : edge frequency, node degree (fringe vertex), node degree (MST included vertex)
    This is identical to modified_prim() with an additional criteria: the degree of the nodes already included in the mst
    arguments:
        graph: a networkx connected graph, nodes must be labelled by integer from 0 to len(graph.nodes) - 1, edge frequency and node degree values must be attached
        src: the source node to start the mst (root in our use case)
        leaves: a list of vertex supposed to be leaves : those are attached after the others
    return:
        parent: a list of integer that hold the parent node of each node in the mst (source parent is -1)
    """
    nodes = list(graph.nodes.keys())
    n = len(nodes)

    key = [(float("inf"), float("inf"), float("inf"))] * n
    parent = [-1] * n  # Keep track of the topology of the mst
    in_mst = [False] * n  # To keep track of vertices included in MST

    # Init pq with the source node
    # Tuples will be sorted in lexicographic order
    pq = []  # queue for internal nodes
    heapq.heappush(pq, (0, 0, 0, 0, src))
    key[src] = 0 # type: ignore

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
        for v in graph[u]:
            if v in leaves:
                continue
            ndeg_out = (
                1 / graph.nodes[v][N_DEGREE]
                if graph.nodes[v][N_DEGREE] > 0
                else float("inf")
            )
            ndeg_in = (
                1 / graph.nodes[u][N_DEGREE]
                if graph.nodes[u][N_DEGREE] > 0
                else float("inf")
            )
            freq = (
                1 / graph[u][v][FREQUENCY_W]
                if graph[u][v][FREQUENCY_W] > 0
                else float("inf")
            )
            weights = (freq, ndeg_out, ndeg_in)
            if not in_mst[v] and key[v] > weights:
                key[v] = weights
                heapq.heappush(pq, (*key[v], v))
                parent[v] = u

    # Attach the leaf nodes
    for u in leaves:
        for v in graph[u]:
            ndeg_in = (
                1 / graph.nodes[u][N_DEGREE]
                if graph.nodes[u][N_DEGREE] > 0
                else float("inf")
            )
            freq = (
                1 / graph[u][v][FREQUENCY_W]
                if graph[u][v][FREQUENCY_W] > 0
                else float("inf")
            )
            weights = (freq, ndeg_in, 0)
            if key[u] > weights:
                key[u] = weights
                parent[u] = v

    return parent_to_mst(parent, graph, src) # type: ignore
