"""
Main Entry Point - Multi-Tool Agent System
"""

from gemini_service import create_agent
from tools import calculator

def main():
    # Get all tools
    tools = [calculator]
    
    # Create agent
    agent = create_agent(tools)
    
    print("Multi-Tool Agent Ready!")
    print(f"Available tools: {', '.join([t.name for t in tools])}")
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