from collections import defaultdict

# empty list for nodes:
vertices = []
vertices_no = 0
# Would it be better to use a matrix to represent the graph?
graph = []
edge_frequencies = defaultdict(int)
all_internal_nodes = []
in_degrees = []


def add_vertex(v):
    """Add a vertex to the graph.

    Args:
        v (int): vertex to add to the graph.
    """
    global graph
    global vertices_no
    global vertices
    global in_degrees
    if v not in vertices:
        vertices_no = vertices_no + 1
        vertices.append(v)
        in_degrees.append(0)
        if vertices_no > 1:
            for vertex in graph:
                vertex.append(0)
        graph.append([0] * vertices_no)


def add_edge(v1, v2, e):
    """Add an edge to the graph.

    Args:
        v1 (int): First vertex of the edge.
        v2 (int): Second vertex of the edge.
        e (int): Edge weight.??
    """
    global graph
    global vertices_no
    global vertices
    global in_degrees
    # edge_frequencies[(v1, v2)] += 1
    # edge_frequencies[(v2, v1)] += 1  # Assuming an undirected graph
    if v1 <= v2:
        edge_frequencies[(v1, v2)] += 1
    else:
        edge_frequencies[(v2, v1)] += 1

    index1 = vertices.index(v1)
    index2 = vertices.index(v2)
    # Check if an edge already exists between v1 and v2
    if graph[index1][index2] != 0:
        graph[index1][index2] = graph[index1][index2] + e
        in_degrees[index2] += 1
    else:
        graph[index1][index2] = e
        in_degrees[index2] += 1
