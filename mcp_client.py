"""
MCP Client - Connect to MCP servers with persistent event loop
Fixed: Proper async handling for LangChain compatibility
"""

import os
import threading
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain.agents import tool
from mcp_tools import MCP_SERVERS

# Global sessions and event loop
calculator_session = None
memory_session = None
weather_session = None
email_session = None  # NEW: Email session
loop = None
loop_thread = None

def get_event_loop():
    """Get or create persistent event loop in background thread"""
    global loop, loop_thread
    
    if loop is None or not loop.is_running():
        loop = asyncio.new_event_loop()
        
        def run_loop():
            asyncio.set_event_loop(loop)
            loop.run_forever()
        
        loop_thread = threading.Thread(target=run_loop, daemon=True)
        loop_thread.start()
    
    return loop

# Connect to Calculator MCP Server
async def connect_calculator():
    """Connect to MCP calculator server"""
    global calculator_session
    
    if calculator_session is None:
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_calculator.py"]
        )
        
        context_manager = stdio_client(server_params)
        read_stream, write_stream = await context_manager.__aenter__()
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
        
        context_manager = stdio_client(server_params)
        read_stream, write_stream = await context_manager.__aenter__()
        memory_session = ClientSession(read_stream, write_stream)
        await memory_session.initialize()
    
    return memory_session

# Connect to Weather MCP Server
async def connect_weather():
    """Connect to MCP weather server"""
    global weather_session
    
    if weather_session is None:
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_weather.py"]
        )
        
        context_manager = stdio_client(server_params)
        read_stream, write_stream = await context_manager.__aenter__()
        weather_session = ClientSession(read_stream, write_stream)
        await weather_session.initialize()
    
    return weather_session

# NEW: Connect to Email MCP Server
async def connect_email():
    """Connect to MCP email server"""
    global email_session
    
    if email_session is None:
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_email.py"]
        )
        
        context_manager = stdio_client(server_params)
        read_stream, write_stream = await context_manager.__aenter__()
        email_session = ClientSession(read_stream, write_stream)
        await email_session.initialize()
    
    return email_session

# Helper function to run async code from sync context
def run_async(coro):
    """Run async coroutine in persistent event loop"""
    loop = get_event_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result(timeout=30)

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
    
    return run_async(call_mcp())

# NEW: EMAIL MCP TOOL

@tool
def mcp_send_email(to_email: str, subject: str, body: str) -> str:
    """Send an email using MCP Email server."""
    if not MCP_SERVERS["gmail"]["enabled"]:
        raise ValueError("MCP Email not enabled")
    
    async def call_mcp():
        session = await connect_email()
        result = await session.call_tool("send_email", {
            "to_email": to_email,
            "subject": subject,
            "body": body
        })
        return result.content[0].text
    
    return run_async(call_mcp())

# WEATHER MCP TOOL

@tool
def mcp_weather(city: str) -> str:
    """Get current weather for a city using MCP Weather server."""
    if not MCP_SERVERS["weather"]["enabled"]:
        raise ValueError("MCP Weather not enabled")
    
    async def call_mcp():
        session = await connect_weather()
        result = await session.call_tool("get_weather", {"city": city})
        return result.content[0].text
    
    return run_async(call_mcp())

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
    
    return run_async(call_mcp())

@tool
def mcp_recall_memory(query: str, num_results: int = 3) -> str:
    """Search and recall memories using MCP Memory server."""
    if not MCP_SERVERS["memory"]["enabled"]:
        raise ValueError("MCP Memory not enabled")
    
    async def call_mcp():
        session = await connect_memory()
        result = await session.call_tool("recall_memory", {"query": query, "num_results": num_results})
        return result.content[0].text
    
    return run_async(call_mcp())

@tool
def mcp_list_all_memories() -> str:
    """List all stored memories using MCP Memory server."""
    if not MCP_SERVERS["memory"]["enabled"]:
        raise ValueError("MCP Memory not enabled")
    
    async def call_mcp():
        session = await connect_memory()
        result = await session.call_tool("list_all_memories", {})
        return result.content[0].text
    
    return run_async(call_mcp())

@tool
def mcp_clear_all_memories() -> str:
    """Delete all stored memories using MCP Memory server."""
    if not MCP_SERVERS["memory"]["enabled"]:
        raise ValueError("MCP Memory not enabled")
    
    async def call_mcp():
        session = await connect_memory()
        result = await session.call_tool("clear_all_memories", {})
        return result.content[0].text
    
    return run_async(call_mcp())

# Get enabled MCP tools
def get_mcp_tools():
    """Returns list of enabled MCP tools"""
    tools = []
    
    # Calculator MCP
    if MCP_SERVERS["calculator"]["enabled"]:
        tools.append(mcp_calculator)
    
    # Weather MCP
    if MCP_SERVERS["weather"]["enabled"]:
        tools.append(mcp_weather)
    
    # NEW: Email MCP
    if MCP_SERVERS["gmail"]["enabled"]:
        tools.append(mcp_send_email)
    
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