"""
MCP Client - Connect to MCP servers
Currently supports: Calculator and Memory
"""

import os
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain.agents import tool
from mcp_tools import MCP_SERVERS

# Global sessions for MCP servers
calculator_session = None
memory_session = None

# Connect to Calculator MCP Server
async def connect_calculator():
    """Connect to MCP calculator server"""
    global calculator_session
    
    if calculator_session is None:
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_calculator.py"]
        )
        
        read_stream, write_stream = await stdio_client(server_params).__aenter__()
        calculator_session = ClientSession(read_stream, write_stream)
        await calculator_session.initialize()
    
    return calculator_session

# Connect to Memory MCP Server
async def connect_memory():
    """Connect to MCP memory server"""
    global memory_session
    
    if memory_session is None:
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_memory.py"]
        )
        
        read_stream, write_stream = await stdio_client(server_params).__aenter__()
        memory_session = ClientSession(read_stream, write_stream)
        await memory_session.initialize()
    
    return memory_session

# CALCULATOR MCP TOOL

@tool
def mcp_calculator(expression: str) -> float:
    """Calculate math expressions using MCP Calculator."""
    if not MCP_SERVERS["calculator"]["enabled"]:
        raise ValueError("MCP Calculator not enabled")
    
    async def call_mcp():
        session = await connect_calculator()
        result = await session.call_tool("calculate", {"expression": expression})
        return result.content[0].text
    
    result = asyncio.run(call_mcp())
    return result

# MEMORY MCP TOOLS

@tool
def mcp_store_memory(content: str, tags: str = "") -> str:
    """Store information in long-term memory using MCP Memory server."""
    if not MCP_SERVERS["memory"]["enabled"]:
        raise ValueError("MCP Memory not enabled")
    
    async def call_mcp():
        session = await connect_memory()
        result = await session.call_tool("store_memory", {"content": content, "tags": tags})
        return result.content[0].text
    
    return asyncio.run(call_mcp())

@tool
def mcp_recall_memory(query: str, num_results: int = 3) -> str:
    """Search and recall memories using MCP Memory server."""
    if not MCP_SERVERS["memory"]["enabled"]:
        raise ValueError("MCP Memory not enabled")
    
    async def call_mcp():
        session = await connect_memory()
        result = await session.call_tool("recall_memory", {"query": query, "num_results": num_results})
        return result.content[0].text
    
    return asyncio.run(call_mcp())

@tool
def mcp_list_all_memories() -> str:
    """List all stored memories using MCP Memory server."""
    if not MCP_SERVERS["memory"]["enabled"]:
        raise ValueError("MCP Memory not enabled")
    
    async def call_mcp():
        session = await connect_memory()
        result = await session.call_tool("list_all_memories", {})
        return result.content[0].text
    
    return asyncio.run(call_mcp())

@tool
def mcp_clear_all_memories() -> str:
    """Delete all stored memories using MCP Memory server."""
    if not MCP_SERVERS["memory"]["enabled"]:
        raise ValueError("MCP Memory not enabled")
    
    async def call_mcp():
        session = await connect_memory()
        result = await session.call_tool("clear_all_memories", {})
        return result.content[0].text
    
    return asyncio.run(call_mcp())

# Get enabled MCP tools
def get_mcp_tools():
    """Returns list of enabled MCP tools"""
    tools = []
    
    # Calculator MCP
    if MCP_SERVERS["calculator"]["enabled"]:
        tools.append(mcp_calculator)
    
    # Memory MCP - adds 4 tools
    if MCP_SERVERS["memory"]["enabled"]:
        tools.extend([
            mcp_store_memory,
            mcp_recall_memory,
            mcp_list_all_memories,
            mcp_clear_all_memories
        ])
    
    return tools

MCP_TOOLS = get_mcp_tools()