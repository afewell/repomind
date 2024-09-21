# main.py

from agents.remi_agent import ReMiAgent
from autogen import Message

def main():
    remi = ReMiAgent()
    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                break
            message = Message(sender='User', content=user_input)
            response_message = remi.handle_message(message)
            print(f"ReMi: {response_message.content}")
    finally:
        remi.close()

if __name__ == "__main__":
    main()
