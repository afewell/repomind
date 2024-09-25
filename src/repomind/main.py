# src/repomind/main.py

from agents.remi_agent import ReMiAgent
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Access your OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise Exception("OpenAI API key not found. Please set it in the .env file.")

def main():
    # LLM configuration
    llm_config = {
        "config_list": [
            {
                "model": "gpt-4",
                "api_key": openai_api_key
            }
        ],
        "timeout": 120,
        "cache_seed": None  # Disable caching for teachability
    }

    remi = ReMiAgent(config_list=llm_config["config_list"])

    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                break
            message = {"role": "user", "content": user_input}
            try:
                response = remi.handle_message(message)
                print(f"ReMi: {response['content']}")
            except Exception as e:
                print(f"An error occurred: {str(e)}")
    finally:
        remi.close()

if __name__ == "__main__":
    main()
