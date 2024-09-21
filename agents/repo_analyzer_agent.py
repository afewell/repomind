import os
import ast
import networkx as nx

class RepoAnalyzerAgent:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.graph = nx.DiGraph()

    def analyze_repository(self):
        print(f"Starting analysis of repository: {self.repo_path}")
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.parse_file(file_path)

    def parse_file(self, file_path):
        print(f"Parsing file: {file_path}")
        with open(file_path, 'r') as f:
            node = ast.parse(f.read(), filename=file_path)
            self.visit_node(node, file_path)

    def visit_node(self, node, file_path):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                self.graph.add_node(child.name, type='class', file=file_path)
            elif isinstance(child, ast.FunctionDef):
                self.graph.add_node(child.name, type='function', file=file_path)
            self.visit_node(child, file_path)

    def save_graph(self, output_path):
        print(f"Saving knowledge graph to: {output_path}")
        nx.write_gpickle(self.graph, output_path)
