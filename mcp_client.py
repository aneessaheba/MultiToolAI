"""
MCP Client - Wraps MCP servers as LangChain tools
Hybrid approach: LangChain agent + MCP servers
"""

import asyncio
from typing import Dict
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain.agents import tool

# Global dictionary to store MCP sessions
_mcp_sessions: Dict[str, ClientSession] = {}
_exit_stacks: Dict[str, any] = {}

async def connect_mcp_server(server_name: str, command: str, args: list):
    """
    Connect to an MCP server and store the session.
    
    Args:
        server_name: Name to identify the server (e.g., "calculator")
        command: Command to run (e.g., "python")
        args: Arguments for the command (e.g., ["mcp_calculator.py"])
    """
    global _mcp_sessions, _exit_stacks
    
    # If already connected, return existing session
    if server_name in _mcp_sessions:
        return _mcp_sessions[server_name]
    
    # Define server parameters
    server_params = StdioServerParameters(
        command=command,
        args=args,
        env=None
    )
    
    # Connect to server
    stdio_transport = stdio_client(server_params)
    stdio, write = await stdio_transport.__aenter__()
    
    # Store exit stack for cleanup
    _exit_stacks[server_name] = stdio_transport
    
    # Create session
    session = ClientSession(stdio, write)
    await session.__aenter__()
    
    # Initialize session
    await session.initialize()
    
    # Store session
    _mcp_sessions[server_name] = session
    
    print(f"✓ Connected to {server_name} MCP server")
    
    return session

async def call_mcp_tool(server_name: str, tool_name: str, arguments: dict) -> str:
    """
    Call a tool on an MCP server.
    
    Args:
        server_name: Name of the server (e.g., "calculator")
        tool_name: Name of the tool (e.g., "calculate")
        arguments: Tool arguments (e.g., {"expression": "5+3"})
    
    Returns:
        Tool result as string
    """
    
    # Get or create session
    if server_name not in _mcp_sessions:
        raise ValueError(f"MCP server '{server_name}' not connected. Call connect_mcp_server first.")
    
    session = _mcp_sessions[server_name]
    
    # Call the tool
    result = await session.call_tool(tool_name, arguments=arguments)
    
    # Extract text from result
    if result.content and len(result.content) > 0:
        return result.content[0].text
    else:
        return "No result returned"

def run_async(coro):
    """
    Helper to run async functions in sync context.
    Needed because LangChain tools are synchronous but MCP is async.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

# LangChain Tool: Calculator
@tool
def mcp_calculator(expression: str) -> str:
    """
    Evaluate mathematical expressions using MCP Calculator Server.
    Use this for any math calculations.
    
    Args:
        expression: Math expression to evaluate (e.g., "5 + 3", "(10 * 2) / 4")
    
    Examples:
        mcp_calculator("5 + 3") returns "8"
        mcp_calculator("10 * 2") returns "20"
    """
    
    async def _calculate():
        # Connect to calculator server if not already connected
        await connect_mcp_server(
            server_name="calculator",
            command="python",
            args=["mcp_calculator.py"]  # No folder - file in root directory
        )
        
        # Call the calculate tool
        result = await call_mcp_tool(
            server_name="calculator",
            tool_name="calculate",
            arguments={"expression": expression}
        )
        
        return result
    
    return run_async(_calculate())

# Export MCP tools for LangChain agent
MCP_TOOLS = [mcp_calculator]

# Cleanup function
async def cleanup_mcp():
    """
    Disconnect from all MCP servers.
    Call this when shutting down.
    """
    global _mcp_sessions, _exit_stacks
    
    for server_name, session in _mcp_sessions.items():
        await session.__aexit__(None, None, None)
        print(f"✓ Disconnected from {server_name}")
    
    for server_name, exit_stack in _exit_stacks.items():
        await exit_stack.__aexit__(None, None, None)
    
    _mcp_sessions = {}
    _exit_stacks = {}