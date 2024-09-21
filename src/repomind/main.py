# main.py

from agents.remi_agent import ReMiAgent

def main():
    remi = ReMiAgent()
    
    # Initialize ReMi
    print("Initializing ReMi...")
    remi.initialize_remi()
    
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
