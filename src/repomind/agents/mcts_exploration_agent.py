# agents/mcts_exploration_agent.py

import networkx as nx
import random
import math
from autogen import Agent

class MCTSNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.action = action
        self.visits = 0
        self.reward = 0.0

    def is_fully_expanded(self, graph):
        return len(self.children) == len(list(graph.neighbors(self.state)))

    def best_child(self, c_param=1.4):
        choices_weights = [
            (child.reward / child.visits) + c_param * math.sqrt((2 * math.log(self.visits) / child.visits))
            for child in self.children
        ]
        return self.children[choices_weights.index(max(choices_weights))]

class MCTSExplorationAgent(Agent):
    def __init__(self, name="Explorer", parent=None, **kwargs):
        super().__init__(name=name, parent=parent, **kwargs)
        self.graph = nx.read_gpickle('storage/repo_graph.gpickle')
        self.max_iterations = 1000
        self.simulation_depth = 10

    def explore(self, issue_description):
        root_state = self.get_initial_state(issue_description)
        root_node = MCTSNode(state=root_state)

        for _ in range(self.max_iterations):
            node = self.tree_policy(root_node)
            reward = self.default_policy(node.state, issue_description)
            self.backup(node, reward)

        best_node = root_node.best_child(c_param=0)
        path = self.extract_action_sequence(best_node)
        response = self.format_response(path)
        return response

    def get_initial_state(self, issue_description):
        # For simplicity, start from a node that is most relevant to the issue description
        # Use BM25 or other relevance scoring to find the most relevant node
        nodes = list(self.graph.nodes(data=True))
        relevance_scores = []
        for node, data in nodes:
            relevance = self.calculate_relevance(issue_description, node, data)
            relevance_scores.append((node, relevance))
        relevance_scores.sort(key=lambda x: x[1], reverse=True)
        initial_state = relevance_scores[0][0]
        return initial_state

    def calculate_relevance(self, issue_description, node_name, node_data):
        # Simple keyword matching for demonstration purposes
        issue_keywords = set(issue_description.lower().split())
        node_keywords = set(node_name.lower().split())
        relevance = len(issue_keywords & node_keywords)
        return relevance

    def tree_policy(self, node):
        while not self.is_terminal(node):
            if not node.is_fully_expanded(self.graph):
                return self.expand(node)
            else:
                node = node.best_child()
        return node

    def expand(self, node):
        tried_children_states = [child.state for child in node.children]
        available_actions = list(self.graph.neighbors(node.state))
        for action in available_actions:
            if action not in tried_children_states:
                child_node = MCTSNode(state=action, parent=node, action=action)
                node.children.append(child_node)
                return child_node
        return node

    def is_terminal(self, node):
        # Define a terminal condition, e.g., maximum depth
        depth = 0
        current = node
        while current.parent is not None:
            current = current.parent
            depth += 1
        return depth >= self.simulation_depth

    def default_policy(self, state, issue_description):
        # Simulate a random walk from the state and return a reward
        current_state = state
        total_reward = 0
        for _ in range(self.simulation_depth):
            neighbors = list(self.graph.neighbors(current_state))
            if not neighbors:
                break
            current_state = random.choice(neighbors)
            reward = self.calculate_relevance(issue_description, current_state, self.graph.nodes[current_state])
            total_reward += reward
        return total_reward

    def backup(self, node, reward):
        while node is not None:
            node.visits += 1
            node.reward += reward
            node = node.parent

    def extract_action_sequence(self, node):
        actions = []
        while node.parent is not None:
            actions.append(node.state)
            node = node.parent
        actions.reverse()
        return actions

    def format_response(self, path):
        # Format the exploration path into a readable response
        response = "Exploration path relevant to your issue:\n"
        for state in path:
            node_data = self.graph.nodes[state]
            response += f"- {state} ({node_data.get('type', 'unknown')}) in {node_data.get('file', 'unknown file')}\n"
        return response
