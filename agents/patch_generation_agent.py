import openai
import os

class PatchGenerationAgent:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def generate_patch(self, context, issue_description):
        print(f"Generating patch for issue: {issue_description}")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an assistant that helps generate code patches."},
                {"role": "user", "content": f"Issue: {issue_description}\nContext: {context}"}
            ]
        )
        return response['choices'][0]['message']['content']
