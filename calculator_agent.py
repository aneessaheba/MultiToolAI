
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import tool, AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from calculator_tool import calculator_tool


# TOOL DEFINITION 

@tool
def calculate(expression: str) -> float:
    """Evaluates a mathematical expression. Example: '5 + 3' returns 8"""
    result = calculator_tool(expression)
    
    if result["success"]:
        return result["result"]
    else:
        raise ValueError(result["error"])


# AGENT SETUP

def create_agent():
    """Creates and returns a calculator agent"""
    
    # Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.environ.get("GOOGLE_API_KEY"),
        temperature=0,
        enable_thought_signatures=True  # Required for Gemini 2.5 Flash
    )
    
    # Define tools
    tools = [calculate]
    
    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a calculator. Use the calculate tool for math questions."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    # Create agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # Return executor
    return AgentExecutor(agent=agent, tools=tools, verbose=False)

# MAIN

def main():
    agent = create_agent()
    
    while True:
        question = input("\nYou: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        if question:
            result = agent.invoke({"input": question})
            print(f"Agent: {result['output']}")

if __name__ == "__main__":
    main()