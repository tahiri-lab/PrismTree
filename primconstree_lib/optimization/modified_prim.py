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
            mst.add_edge(i, p, avglen=graph[i][p][AVG_LEN], frequency=graph[i][p][FREQUENCY_W])
    
    return mst

# based on https://www.geeksforgeeks.org/prims-algorithm-using-priority_queue-stl/
def modified_prim(graph: nx.Graph, src: int) -> list[int]:
    """
    Create a maximum spanning tree using an adapted implementation of prim with priority queue
    The following criteria are maximised (from highest to least priority) : edge frequency, node degree (fringe vertex)
    arguments:
        graph: a networkx connected graph, nodes must be labelled by integer from 0 to len(graph.nodes) - 1, edge frequency and node degree values must be attached
        src: the source node to start the mst (root in our use case)
    return:
        parent: a list of integer that hold the parent node of each node in the mst (source parent is -1)
    """
    nodes = list(graph.nodes.keys())
    n = len(nodes)

    # Initialize keys of all vertices as infinite and parent of every vertex as -1
    key = [(float('inf'), float('inf'))] * n
    parent = [-1] * n
    in_mst = [False] * n       # To keep track of vertices included in MST

    # Priority queue to store vertices that are being processed
    # Every item is a pair (weight, vertex)
    # First key (weight), is used by default to compare items
    pq = []  

    # Insert source itself into the priority queue and initialize its key as 0
    heapq.heappush(pq, (0, 0, src))
    key[src] = 0

    # Loop until the priority queue becomes empty
    while pq:
        # The first vertex in the pair is the minimum key vertex
        # Extract it from the priority queue
        # The vertex label is stored in the second of the pair
        u = heapq.heappop(pq)[-1]

        # Different key values for the same vertex may exist in the priority queue.
        # The one with the least key value is always processed first.
        # Therefore, ignore the rest.
        if in_mst[u]:
            continue

        in_mst[u] = True  # Include the vertex in MST

        # Iterate through all adjacent vertices of a vertex
        for v in graph[u]:
            # If v is not in MST and the weight of (u, v) is smaller than the current key of v
            ndeg = 1/graph.nodes[v][N_DEGREE] if graph.nodes[v][N_DEGREE] > 0 else float('inf')
            weights = (1/graph[u][v][FREQUENCY_W], ndeg)
            if not in_mst[v] and key[v] > weights:
                # Update the key of v
                key[v] = weights
                heapq.heappush(pq, (key[v][0], key[v][1], v))
                parent[v] = u

    return parent_to_mst(parent, graph, src)


# based on https://www.geeksforgeeks.org/prims-algorithm-using-priority_queue-stl/
def modified_modified_prim(graph: nx.Graph, src: int) -> list[int]:
    """
    Create a maximum spanning tree using an adapted implementation of prim with priority queue
    The following criteria are maximised (from highest to least priority) : edge frequency, node degree (fringe vertex), node degree (MST included vertex)
    This is identical to modified_prim() with an additional criteria: the degree of the nodes already included in the mst
    arguments:
        graph: a networkx connected graph, nodes must be labelled by integer from 0 to len(graph.nodes) - 1, edge frequency and node degree values must be attached
        src: the source node to start the mst (root in our use case)
    return:
        parent: a list of integer that hold the parent node of each node in the mst (source parent is -1)
    """
    nodes = list(graph.nodes.keys())
    n = len(nodes)

    # Initialize keys of all vertices as infinite and parent of every vertex as -1
    key = [(float('inf'), float('inf'))] * n
    parent = [-1] * n
    in_mst = [False] * n       # To keep track of vertices included in MST

    # Priority queue to store vertices that are being processed
    # Every item is a pair (weight, vertex)
    # First key (weight), is used by default to compare items
    pq = []  

    # Insert source itself into the priority queue and initialize its key as 0
    heapq.heappush(pq, (0, 0, 0, src))
    key[src] = 0

    # Loop until the priority queue becomes empty
    while pq:
        # The first vertex in the pair is the minimum key vertex
        # Extract it from the priority queue
        # The vertex label is stored in the second of the pair
        u = heapq.heappop(pq)[-1]

        # Different key values for the same vertex may exist in the priority queue.
        # The one with the least key value is always processed first.
        # Therefore, ignore the rest.
        if in_mst[u]:
            continue

        in_mst[u] = True  # Include the vertex in MST

        # Iterate through all adjacent vertices of a vertex
        for v in graph[u]:
            # If v is not in MST and the weight of (u, v) is smaller than the current key of v
            ndeg_out = 1/graph.nodes[v][N_DEGREE] if graph.nodes[v][N_DEGREE] > 0 else float('inf')
            ndeg_in = 1/graph.nodes[u][N_DEGREE] if graph.nodes[u][N_DEGREE] > 0 else float('inf')
            weights = (1/graph[u][v][FREQUENCY_W], ndeg_out, ndeg_in)
            if not in_mst[v] and key[v] > weights:
                # Update the key of v
                key[v] = weights
                heapq.heappush(pq, (*key[v], v))
                parent[v] = u

    return parent_to_mst(parent, graph, src)