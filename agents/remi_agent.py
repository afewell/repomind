# agents/remi_agent.py

import os
import json
from autogen import TeachableAgent, Message
from agents.repo_analyzer_agent import RepoAnalyzerAgent
from agents.mcts_exploration_agent import MCTSExplorationAgent
from agents.patch_generation_agent import PatchGenerationAgent
from filelock import FileLock

class ReMiAgent(TeachableAgent):
    def __init__(self, name="ReMi", **kwargs):
        super().__init__(name=name, **kwargs)
        self.memory_file = 'storage/remi_memory.json'
        self.lock_file = 'storage/remi_lock.lock'
        self.lock = FileLock(self.lock_file)
        self.in_read_only = False
        self.check_session_lock()
        self.load_memory()
        self.supporting_agents = {}
        self.setup_supporting_agents()

    def check_session_lock(self):
        try:
            self.lock.acquire(timeout=1)
            print("Session started in write mode.")
        except:
            self.in_read_only = True
            print("Another session is active. Starting in read-only mode.")

    def load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
        else:
            self.memory = {}

    def save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f)

    def setup_supporting_agents(self):
        self.supporting_agents = {
            'RepoAnalyzer': RepoAnalyzerAgent(parent=self),
            'Explorer': MCTSExplorationAgent(parent=self),
            'PatchGenerator': PatchGenerationAgent(parent=self)
        }

    def handle_message(self, message):
        if message.content.lower() == 'initialize':
            self.initialize_remi()
            return Message(sender=self.name, content="Initialization complete.")
        else:
            # Process other messages
            return self.process_user_request(message.content)

    def initialize_remi(self):
        print("Welcome to RepoMind! Let's get started with the initialization.")
        target_repo = input("Please enter the GitHub repository URL you want ReMi to analyze: ")
        self.memory['target_repo'] = target_repo
        self.save_memory()
        # Start repository analysis
        self.supporting_agents['RepoAnalyzer'].analyze_repository(target_repo)
        print("Repository analysis complete.")
        # Additional initialization steps as needed

    def process_user_request(self, request):
        # Use supporting agents to handle the request
        if 'question' in request.lower():
            response = self.supporting_agents['Explorer'].explore(request)
            return Message(sender=self.name, content=response)
        elif 'generate patch' in request.lower():
            context = "Relevant code context"
            response = self.supporting_agents['PatchGenerator'].generate_patch(context, request)
            return Message(sender=self.name, content=response)
        else:
            return Message(sender=self.name, content="I'm sorry, I didn't understand that request.")

    def close(self):
        if not self.in_read_only:
            self.lock.release()
            print("Session ended. Lock released.")
        self.save_memory()
