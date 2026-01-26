"""
Gemini Service - Handles LLM configuration and agent creation
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from tools import ALL_TOOLS

# Load environment variables
load_dotenv()

# Available tools
TOOLS = ALL_TOOLS

def get_llm():
    """Initialize and return Gemini LLM"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.environ.get("GOOGLE_API_KEY"),
        temperature=0,
        enable_thought_signatures=True
    )

def create_agent():
    """Create agent with all available tools"""
    
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant with access to various tools. Use them when needed."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, TOOLS, prompt)
    return AgentExecutor(agent=agent, tools=TOOLS, verbose=True)