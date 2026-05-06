import sys
from agent import run_builder

def main():
    """
    Main entry point for the Scaler Agent CLI.
    """
    banner = r"""
╔══════════════════════════════════════════════════════╗
║              SCALER AGENT - CLI TOOL                 ║
║       The Ultimate AI Web Cloning Specialist         ║
╚══════════════════════════════════════════════════════╝
    """
    print(banner)
    print("Welcome! Type your instructions (e.g., 'Clone Scaler website').")
    print("Type 'exit' or 'quit' to stop.")
    
    while True:
        try:
            user_input = input("\n\033[1;36mYou: \033[0m").strip()
            
            if user_input.lower() in ["exit", "quit"]:
                print("\nGoodbye! See you next time.")
                break
            
            if not user_input:
                continue
                
            # Run the agent builder
            run_builder(user_input)
            
        except KeyboardInterrupt:
            print("\n\nSession terminated by user. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n[CRITICAL ERROR] An error occurred in the main loop: {str(e)}")

if __name__ == "__main__":
    main()
