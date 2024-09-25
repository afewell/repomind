import pickle
import os
import networkx as nx

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
graph_path = os.path.join(BASE_DIR, 'storage', 'repo_graph.gpickle')

# Load the graph
with open(graph_path, 'rb') as f:
    graph = pickle.load(f)

# Print basic information about the graph
print("Nodes in the graph:", len(graph.nodes))
print("Edges in the graph:", len(graph.edges))

# Optionally, print the nodes and edges to inspect them
print("Sample nodes:", list(graph.nodes(data=True))[:50])  # Show 10 sample nodes with attributes
print("Sample edges:", list(graph.edges(data=True))[:50])  # Show 10 sample edges with attributes
