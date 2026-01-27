"""
MCP Memory Client - Connects to MCP Memory Server
"""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain.agents import tool
from contextlib import asynccontextmanager

class MCPMemoryClient:
    """Client for MCP Memory Server with auto-start capability"""
    
    def __init__(self):
        self.session = None
        self.exit_stack = None
        
    async def connect(self):
        """Connect to MCP Memory Server (auto-starts via npx)"""
        
        # Server parameters - runs npx command to start memory server
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-memory"],
            env=None
        )
        
        # Create context manager for stdio connection
        stdio_transport = stdio_client(server_params)
        self.exit_stack = stdio_transport
        
        # Connect
        stdio, write = await self.exit_stack.__aenter__()
        self.session = ClientSession(stdio, write)
        
        # Initialize session
        await self.session.__aenter__()
        
        # Initialize the server
        await self.session.initialize()
        
        print("✓ MCP Memory Server connected and initialized")
        
        return self.session
    
    async def disconnect(self):
        """Disconnect from server"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self.exit_stack:
            await self.exit_stack.__aexit__(None, None, None)
        print("✓ MCP Memory Server disconnected")
    
    async def create_entities(self, entities: list) -> str:
        """
        Create entities in knowledge graph
        
        Args:
            entities: List of dicts with 'name', 'entityType', 'observations'
        """
        result = await self.session.call_tool(
            "create_entities",
            arguments={"entities": entities}
        )
        return result.content[0].text if result.content else "Entities created"
    
    async def create_relations(self, relations: list) -> str:
        """
        Create relations between entities
        
        Args:
            relations: List of dicts with 'from', 'to', 'relationType'
        """
        result = await self.session.call_tool(
            "create_relations",
            arguments={"relations": relations}
        )
        return result.content[0].text if result.content else "Relations created"
    
    async def search_nodes(self, query: str) -> str:
        """
        Search for nodes in knowledge graph
        
        Args:
            query: Search query
        """
        result = await self.session.call_tool(
            "search_nodes",
            arguments={"query": query}
        )
        return result.content[0].text if result.content else "No results found"
    
    async def read_graph(self) -> str:
        """Read entire knowledge graph"""
        result = await self.session.call_tool(
            "read_graph",
            arguments={}
        )
        return result.content[0].text if result.content else "Graph is empty"

# Global client instance
_mcp_client = None

async def get_mcp_client():
    """Get or create MCP client singleton"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPMemoryClient()
        await _mcp_client.connect()
    return _mcp_client

# Synchronous wrappers for LangChain tools

def run_async(coro):
    """Helper to run async functions synchronously"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

@tool
def store_memory(content: str, entity_type: str = "fact") -> str:
    """
    Store information in long-term memory using MCP Knowledge Graph.
    Use this when the user asks you to remember something.
    
    Args:
        content: The information to remember (e.g., "User loves pepperoni pizza")
        entity_type: Type of entity (fact, preference, person, place, etc.)
    
    Examples:
        - store_memory("User's favorite color is blue", "preference")
        - store_memory("Meeting with John on Monday at 3pm", "event")
        - store_memory("User allergic to peanuts", "health")
    """
    try:
        async def _store():
            client = await get_mcp_client()
            
            # Create entity with observation
            entities = [{
                "name": f"memory_{entity_type}",
                "entityType": entity_type,
                "observations": [content]
            }]
            
            result = await client.create_entities(entities)
            return f"✓ Memory stored successfully! I'll remember: '{content}'"
        
        return run_async(_store())
    
    except Exception as e:
        return f"Failed to store memory: {str(e)}"

@tool
def recall_memory(query: str) -> str:
    """
    Search and recall memories from knowledge graph.
    Use this when the user asks you to remember or recall something.
    
    Args:
        query: What to search for (e.g., "food preferences", "meetings", "health info")
    
    Examples:
        - recall_memory("What did I say about food?")
        - recall_memory("My schedule")
        - recall_memory("health information")
    """
    try:
        async def _recall():
            client = await get_mcp_client()
            result = await client.search_nodes(query)
            
            if not result or result == "No results found":
                return "No memories found related to your query."
            
            return f"I found relevant memories:\n\n{result}"
        
        return run_async(_recall())
    
    except Exception as e:
        return f"Failed to recall memories: {str(e)}"

@tool
def list_all_memories() -> str:
    """
    List all stored memories from knowledge graph.
    Use this when the user wants to see everything you remember.
    
    Example: "Show me all my memories" or "What do you remember about me?"
    """
    try:
        async def _list():
            client = await get_mcp_client()
            result = await client.read_graph()
            
            if not result or "empty" in result.lower():
                return "I don't have any memories stored yet."
            
            return f"Here are all my memories:\n\n{result}"
        
        return run_async(_list())
    
    except Exception as e:
        return f"Failed to list memories: {str(e)}"

# Export memory tools
MEMORY_TOOLS = [store_memory, recall_memory, list_all_memories]

# Cleanup function
async def cleanup_mcp():
    """Call this on shutdown"""
    global _mcp_client
    if _mcp_client:
        await _mcp_client.disconnect()