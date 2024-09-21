# agents/patch_generation_agent.py

import openai
from autogen import Agent

class PatchGenerationAgent(Agent):
    def __init__(self, name="PatchGenerator", parent=None, **kwargs):
        super().__init__(name=name, parent=parent, **kwargs)
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def generate_patch(self, context, issue_description):
        prompt = f"Context: {context}\nIssue: {issue_description}\nGenerate a code patch to address the issue."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an assistant that helps generate code patches."},
                {"role": "user", "content": prompt}
            ]
        )
        patch = response['choices'][0]['message']['content']
        return patch
