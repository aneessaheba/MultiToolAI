"""
Gemini Service - Handles LLM configuration and agent creation
Hybrid approach: Combines regular tools + MCP tools
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
try:
    from langchain.agents import AgentExecutor, create_tool_calling_agent
except ImportError:
    from langchain.agents import AgentExecutor, create_react_agent as create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate

# Import regular tools
from tools import ALL_TOOLS

# Import MCP tools (wrapped as LangChain tools)
from mcp_client import MCP_TOOLS

load_dotenv()

# Combine regular tools + MCP tools
TOOLS = ALL_TOOLS + MCP_TOOLS

def get_llm():
    """Initialize and return Gemini LLM"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.environ.get("GOOGLE_API_KEY"),
        temperature=0,
        enable_thought_signatures=True
    )

def create_agent():
    """
    Create agent with all available tools.
    Now includes both regular Python tools and MCP tools.
    """
    llm = get_llm()
    
    # System prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant with access to various tools.

Available tools include:
- Regular tools: calculator, weather, wikipedia, google_search, web_scraper, email, summarizer
- MCP tools: mcp_calculator (uses MCP server for calculations)

Use the appropriate tool when needed to help the user."""),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, TOOLS, prompt)
    return AgentExecutor(agent=agent, tools=TOOLS, verbose=True)