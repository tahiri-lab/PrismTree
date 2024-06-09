# vertices = []
# vertices_no = 0
# graph = []
# edge_frequencies = defaultdict(int)
# all_internal_nodes = []
# in_degrees = []


# def identify_nodes(tree):
#     leaf_nodes = []
#     for node in tree.traverse("postorder"):
#         if node.is_leaf():
#             leaf_nodes.append(node.name)
#     return leaf_nodes


# def add_vertex(v):
#     global graph
#     global vertices_no
#     global vertices
#     global in_degrees
#     if v not in vertices:
#         vertices_no = vertices_no + 1
#         vertices.append(v)
#         in_degrees.append(0)
#         if vertices_no > 1:
#             for vertex in graph:
#                 vertex.append(0)
#         graph.append([0] * vertices_no)


# def add_edge(v1, v2, e):
#     global graph
#     global vertices_no
#     global vertices
#     global in_degrees
#     # edge_frequencies[(v1, v2)] += 1
#     # edge_frequencies[(v2, v1)] += 1  # Assuming an undirected graph
#     if v1 <= v2:
#         edge_frequencies[(v1, v2)] += 1
#     else:
#         edge_frequencies[(v2, v1)] += 1

#     index1 = vertices.index(v1)
#     index2 = vertices.index(v2)
#     # Check if an edge already exists between v1 and v2
#     if graph[index1][index2] != 0:
#         graph[index1][index2] = graph[index1][index2] + e
#         in_degrees[index2] += 1
#         # print(v1," to ", v2, " more than once\n\n")
#     else:
#         graph[index1][index2] = e
#         in_degrees[index2] += 1
#         # print(v1," to ", v2, "\n\n")
#     # print("graph is now as: ",graph)


# def update_internal_node_names(tree, leaf_nodes):
#     internal_nodes = []

#     def generate_unique_name(name):
#         # Generate a unique name by adding a suffix
#         suffix = 1
#         while name + str(suffix) in leaf_nodes:
#             suffix += 1
#         return name + str(suffix)

#     def update_internal_node(node):
#         if not node.is_leaf():
#             children_names = sorted([child.name for child in node.children])
#             new_name = "".join(children_names)
#             new_name = "".join(sorted(new_name))
#             if new_name in leaf_nodes:
#                 new_name = generate_unique_name(new_name)
#             node.name = new_name
#             internal_nodes.append(node.name)
#             if node.name not in all_internal_nodes:
#                 all_internal_nodes.append(node.name)

#     for node in tree.traverse("postorder"):
#         update_internal_node(node)
#     return internal_nodes


# def check_direct_connection(tree, v1, v2):
#     # Find the nodes by name
#     node1 = tree.search_nodes(name=v1)
#     node2 = tree.search_nodes(name=v2)
#     # print("\n", v1, node1,node1[0], " and ",v2,node2,"\n")
#     if not node1 or not node2:
#         print("they does not exits")
#         return False  # One of the nodes does not exist

#     node1 = node1[0]
#     node2 = node2[0]
#     # print("\ncheck_direct_connection :", node1, "-", node1[0],"\n")
#     # Check if node1 is the parent of node2
#     if node2.up == node1:  # or node1.up == node2
#         # print()
#         # print(node1, "is parent of ",node2)
#         # print()
#         return True
#     return False


# def calculate_distances(tree):
#     distances = {}
#     all_nodes = list(tree.traverse())  # Collect all nodes
#     for i in range(len(all_nodes)):
#         for j in range(i + 1, len(all_nodes)):
#             node1 = all_nodes[i]
#             node2 = all_nodes[j]
#             distance = node1.get_distance(
#                 node2
#             )  # Calculate distance using the tree library function
#             distance = round(distance, 2)
#             distances[(node1.name, node2.name)] = distance
#             distances[(node2.name, node1.name)] = (
#                 distance  # Optionally, for undirected graphs
#             )
#     return distances


# def tree_to_graph(tree):
#     # Get a list of all unique nodes (leaves and internal nodes)
#     # print(tree)
#     unique_nodes = set(tree.iter_leaves())
#     unique_nodes.update(tree.traverse("preorder"))

#     # Create a matrix to represent the distances
#     node_names = [node.name for node in unique_nodes]  # Define node_names here
#     node_names.sort(key=lambda x: (tree & x).get_distance(tree))
#     print("node_names : ", node_names)

#     distances = calculate_distances(tree)

#     # add vertex
#     for node in node_names:
#         add_vertex(node)

#     # add edge
#     for i in range(0, len(node_names)):
#         for j in range(i + 1, len(node_names)):
#             v1 = node_names[i]
#             v2 = node_names[j]
#             if check_direct_connection(tree, v1, v2):
#                 distance = round(distances.get((v1, v2), 0), 2)
#                 # print("\n\nTree nodes conection : ",v1,"-",v2,"-",distance,"\n")
#                 add_edge(v1, v2, distance)


# input_file = (
#     r"C:\Users\harsh\s\PrimConsTree\PrimConsTree\datasets\simulated\Trex_trees20.txt"
# )
# with open(input_file, "r") as file:
#     for idx, line in enumerate(file, 1):
#         tree = Tree(line.strip(), format=1)
#         leaf_nodes = identify_nodes(tree)
#         # print(leaf_nodes)
#         internal_nodes = update_internal_node_names(tree, leaf_nodes)
#         # print(internal_nodes)
#         tree_to_graph(tree)


# print("Combined Graph In-degrees:", in_degrees)

# # print('\nnumber of internal nodes:',len(internal_nodes))
# print("\n number of all internal nodes:", len(all_internal_nodes))
# print("\n all internal nodes:", all_internal_nodes)
# print("\n all vertices:", vertices)
# print("\n number of vertices:", vertices_no)

# for i in range(vertices_no):
#     print(vertices[i], end="-")
#     print(in_degrees[i])

# # Extract unique node names
# nodes = sorted(set(node for edge in edge_frequencies for node in edge))
# num_nodes = len(nodes)
# print("\n nodes:", nodes)
# print("\n number of nodes:", len(nodes))


# # Generate nodes list and initialize matrix
# nodes = sorted(set(node for edge in edge_frequencies for node in edge))
# num_nodes = len(nodes)
# print("\nNodes:", nodes)
# print("\nNumber of nodes:", num_nodes)

# # Initialize the frequency matrix
# frequency_matrix = [[0] * num_nodes for _ in range(num_nodes)]

# # Mapping node names to indices
# node_index_map = {node: index for index, node in enumerate(nodes)}

# # Populate the frequency matrix
# for (node1, node2), freq in edge_frequencies.items():
#     index1 = node_index_map[node1]
#     index2 = node_index_map[node2]
#     # Since it's an undirected graph, symmetrize the entries
#     frequency_matrix[index1][index2] = frequency_matrix[index2][index1] = freq

# # Print frequencies between each pair
# for i in range(num_nodes):
#     for j in range(num_nodes):  # Start from i to avoid duplicating prints
#         if frequency_matrix[i][j] != 0:
#             print(
#                 f"Frequency between {nodes[i]} and {nodes[j]}: {frequency_matrix[i][j]}"
#             )


# for i in range(vertices_no):
#     for j in range(vertices_no):
#         if graph[i][j] != 0 and frequency_matrix[i][j] != 0:
#             graph[i][j] = round(graph[i][j] / frequency_matrix[i][j], 2)
#             # print("Hi ",graph[i][j])

# print("frequency_matrix : ", frequency_matrix)
# for i in graph:
#     print(i)
