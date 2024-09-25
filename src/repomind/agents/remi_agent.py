# src/repomind/agents/remi_agent.py

import os
import json
from autogen import ConversableAgent
from autogen.agentchat.contrib.capabilities.teachability import Teachability
from agents.repo_analyzer_agent import RepoAnalyzerAgent
from filelock import FileLock

# Determine the base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class ReMiAgent(ConversableAgent):
    def __init__(self, name="ReMi", **kwargs):
        super().__init__(
            name=name,
            llm_config={
                "config_list": kwargs.get("config_list"),
                "timeout": 120,
                "cache_seed": None  # Disable caching for teachability
            }
        )
        # Update file paths to use the base directory
        self.memory_file = os.path.join(BASE_DIR, 'storage', 'remi_memory.json')
        self.lock_file = os.path.join(BASE_DIR, 'storage', 'remi_lock.lock')
        self.lock = FileLock(self.lock_file)
        self.in_read_only = False
        self.check_session_lock()
        self.load_memory()
        self.supporting_agents = {}
        self.initialized = self.memory.get('initialized', False)
        if self.initialized:
            self.setup_supporting_agents()
        # Instantiate Teachability
        self.teachability = Teachability(
            verbosity=0,
            reset_db=False,
            path_to_db_dir=os.path.join(BASE_DIR, 'storage', 'teachability_db'),
            recall_threshold=1.5  # Adjust as needed
        )
        # Add teachability to the agent
        self.teachability.add_to_agent(self)

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
        from agents.mcts_exploration_agent import MCTSExplorationAgent
        from agents.patch_generation_agent import PatchGenerationAgent

        self.supporting_agents['Explorer'] = MCTSExplorationAgent(parent=self)
        self.supporting_agents['PatchGenerator'] = PatchGenerationAgent(parent=self)

    def initialize_remi(self):
        if not self.initialized:
            print("Welcome to RepoMind! Let's get started with the initialization.")
            target_repo = input("Please enter the GitHub repository URL you want ReMi to analyze: ")
            self.memory['target_repo'] = target_repo
            self.save_memory()
            # Start repository analysis
            analyzer = RepoAnalyzerAgent(parent=self)
            analyzer.analyze_repository(target_repo)
            print("Repository analysis complete.")
            # Now, initialize the supporting agents that depend on the graph
            self.setup_supporting_agents()
            self.memory['initialized'] = True
            self.initialized = True
            self.save_memory()
        else:
            print("ReMi has already been initialized.")

    def handle_message(self, message):
        user_input = message['content'].strip()
        if not self.initialized:
            if user_input.lower() == 'initialize':
                self.initialize_remi()
                return {"role": self.name, "content": "Initialization complete."}
            else:
                return {"role": self.name, "content": "ReMi is not initialized yet. Please type 'initialize' to begin the setup process."}
        else:
            return self.process_user_request(user_input)

    def process_user_request(self, request):
        if 'question' in request.lower():
            response = self.supporting_agents['Explorer'].explore(request)
            return {"role": self.name, "content": response}
        elif 'generate patch' in request.lower():
            context = self.supporting_agents['Explorer'].explore(request)
            response = self.supporting_agents['PatchGenerator'].generate_patch(context, request)
            return {"role": self.name, "content": response}
        else:
            # Use the agent's generate_reply method to handle general queries
            messages = [{'role': 'user', 'content': request}]
            response = self.generate_reply(messages)
            return {"role": self.name, "content": response}

    def close(self):
        if not self.in_read_only:
            self.lock.release()
            print("Session ended. Lock released.")
        self.save_memory()
