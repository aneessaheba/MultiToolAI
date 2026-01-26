"""
Main Entry Point - Multi-Tool Agent System
"""

from gemini_service import create_agent, TOOLS

def main():
    # Create agent
    agent = create_agent()
    
    print("Multi-Tool Agent Ready!")
    print(f"Available tools: {', '.join([t.name for t in TOOLS])}")
    print("Type 'quit' to exit\n")
    
    while True:
        question = input("\nYou: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        if question:
            result = agent.invoke({"input": question})
            print(f"\nAgent: {result['output']}")

if __name__ == "__main__":
    main()