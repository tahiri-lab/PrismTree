import networkx as nx
import matplotlib.pyplot as plt
import random
import heapq
from modified_prim import modified_modified_prim, modified_prim

FREQUENCY_W = "frequency"
N_DEGREE = "ndegree"
AVG_LEN = "avglen"

def drawgraph(G):

    # Print nodes with their attributes
    print("Nodes with attributes:")
    for node, data in G.nodes(data=True):
        print(f"Node {node}: ndegree = {data['ndegree']}")
        
    # Draw the graph with edge frequency reflected in edge width
    edge_widths = [data['frequency'] for u, v, data in G.edges(data=True)]
    pos = nx.spring_layout(G)  # Layout for the graph

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500)

    # Draw edges with edge width based on frequency attribute
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='gray')

    # Draw edge labels (optional)
    edge_labels = {(u, v): data['frequency'] for u, v, data in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    # Draw node labels
    nx.draw_networkx_labels(G, pos, font_weight='bold')

    # Display the graph
    plt.title('Graph with Edge Frequency')
    plt.axis('off')
    plt.show()


def random_graph():
    # Create an empty graph
    G = nx.Graph()

    # Add nodes with ndegree attribute ranging from 1 to 10
    for i in range(0, 9):
        ndegree_value = random.randint(1, 10)
        G.add_node(i, ndegree=ndegree_value)

    # Add edges with frequency (positive integer) and avglen (positive float) attributes
    # Ensure that each edge is unique by adding an attribute that makes it unique
    edge_counter = 1

    for i in range(0, 9):
        for j in range(i+1, 9):
            if random.randint(1, 10) > 7:
                frequency_value = random.randint(1, 10)
                avglen_value = random.uniform(1.0, 10.0)
                G.add_edge(i, j, frequency=frequency_value, avglen=avglen_value, edge_id=edge_counter)
                edge_counter += 1

    return G

def my_graph():
    G = nx.Graph()
    G.add_node(0, ndegree=1)
    G.add_node(1, ndegree=2)
    G.add_node(2, ndegree=4)
    G.add_node(3, ndegree=1)
    G.add_node(4, ndegree=3)
    G.add_node(5, ndegree=4)
    G.add_node(6, ndegree=1)
    G.add_edge(0,1, frequency=5, avglen=5)
    G.add_edge(0,2, frequency=4, avglen=5)
    G.add_edge(0,3, frequency=5, avglen=5)
    G.add_edge(1,4, frequency=3, avglen=5)
    G.add_edge(2,4, frequency=3, avglen=5)
    G.add_edge(2,5, frequency=2, avglen=5)
    G.add_edge(3,5, frequency=2, avglen=5)
    G.add_edge(4,6, frequency=1, avglen=5)
    G.add_edge(5,6, frequency=1, avglen=5)
    return G

def example():
    G = my_graph()
    drawgraph(G)

    root = 0
    mst = modified_modified_prim(G, root)
    drawgraph(mst)

example()
