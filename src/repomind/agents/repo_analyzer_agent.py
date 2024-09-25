# agents/repo_analyzer_agent.py

import os
import subprocess
import pickle
import networkx as nx
import ast
from autogen import Agent

# Determine the base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class RepoAnalyzerAgent(Agent):
    def __init__(self, name="RepoAnalyzer", parent=None, **kwargs):
        super().__init__(name=name, parent=parent, **kwargs)
        self.graph = nx.DiGraph()

    def analyze_repository(self, repo_url):
        # Clone the repository
        repo_path = self.clone_repository(repo_url)
        # Build the knowledge graph
        self.build_knowledge_graph(repo_path)
        # Save the graph to the storage directory in the base directory
        graph_path = os.path.join(BASE_DIR, 'storage', 'repo_graph.gpickle')
        # Make sure the 'storage' directory exists
        os.makedirs(os.path.dirname(graph_path), exist_ok=True)
        # Save the graph using pickle
        with open(graph_path, 'wb') as f:
            pickle.dump(self.graph, f)
        print("Knowledge graph saved.")
        # Now you can read the graph if needed (this might not be necessary right after saving)
        with open(graph_path, 'rb') as f:
            self.graph = pickle.load(f)

    def clone_repository(self, repo_url):
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        # Clone the repository into the data directory in the base directory
        repo_path = os.path.join(BASE_DIR, 'data', repo_name)
        if not os.path.exists(repo_path):
            subprocess.run(['git', 'clone', repo_url, repo_path])
        return repo_path

    def build_knowledge_graph(self, repo_path):
        """Parse files and build a knowledge graph of the repository."""
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.parse_file(file_path)

    def parse_file(self, file_path):
        """Parse a Python file and add nodes and edges to the graph."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                node = ast.parse(f.read(), filename=file_path)
                self.visit_node(node, file_path)
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def visit_node(self, node, file_path, parent=None):
        """Recursively visit AST nodes and build the graph."""
        if isinstance(node, ast.ClassDef):
            # Add the class as a node
            self.graph.add_node(node.name, type='class', file=file_path)
            # If there's a parent, add an edge between the parent and the current node
            if parent:
                self.graph.add_edge(parent, node.name, relationship='contains')
            parent = node.name  # Set the parent to the current class
        elif isinstance(node, ast.FunctionDef):
            # Add the function as a node
            self.graph.add_node(node.name, type='function', file=file_path)
            # If there's a parent (class or another function), add an edge
            if parent:
                self.graph.add_edge(parent, node.name, relationship='contains')

        # Visit child nodes recursively
        for child in ast.iter_child_nodes(node):
            self.visit_node(child, file_path, parent)