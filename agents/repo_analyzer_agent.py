# agents/repo_analyzer_agent.py

import os
import subprocess
import networkx as nx
import ast
from autogen import Agent

class RepoAnalyzerAgent(Agent):
    def __init__(self, name="RepoAnalyzer", parent=None, **kwargs):
        super().__init__(name=name, parent=parent, **kwargs)
        self.graph = nx.DiGraph()

    def analyze_repository(self, repo_url):
        repo_path = self.clone_repository(repo_url)
        self.build_knowledge_graph(repo_path)
        nx.write_gpickle(self.graph, 'storage/repo_graph.gpickle')
        print("Knowledge graph saved.")

    def clone_repository(self, repo_url):
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        repo_path = os.path.join('data', repo_name)
        if not os.path.exists(repo_path):
            subprocess.run(['git', 'clone', repo_url, repo_path])
        return repo_path

    def build_knowledge_graph(self, repo_path):
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.parse_file(file_path)

    def parse_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                node = ast.parse(f.read(), filename=file_path)
                self.visit_node(node, file_path)
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def visit_node(self, node, file_path):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                self.graph.add_node(child.name, type='class', file=file_path)
            elif isinstance(child, ast.FunctionDef):
                self.graph.add_node(child.name, type='function', file=file_path)
            self.visit_node(child, file_path)
