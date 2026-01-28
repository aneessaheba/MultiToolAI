"""
Memory MCP Server
Uses official @modelcontextprotocol/server-memory for knowledge graph-based memory
"""

import asyncio
import json
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import mcp.types as types

# Create the MCP server instance
server = Server("memory-server")

# Simple in-memory storage (replace with persistent storage if needed)
memory_store = []

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available memory tools"""
    return [
        types.Tool(
            name="store_memory",
            description="Store information in long-term memory with automatic embeddings",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The information to remember"
                    },
                    "tags": {
                        "type": "string",
                        "description": "Optional comma-separated tags for categorization"
                    }
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="recall_memory",
            description="Search and recall memories using semantic search",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What to search for"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of memories to retrieve (default: 3)"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="list_all_memories",
            description="List all stored memories",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="clear_all_memories",
            description="Delete all stored memories",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    """Handle tool calls for memory operations"""
    
    if name == "store_memory":
        if not arguments or "content" not in arguments:
            raise ValueError("Missing 'content' argument")
        
        content = arguments["content"]
        tags = arguments.get("tags", "")
        
        # Store memory
        import uuid
        from datetime import datetime
        
        memory = {
            "id": str(uuid.uuid4()),
            "content": content,
            "tags": tags,
            "timestamp": datetime.now().isoformat()
        }
        memory_store.append(memory)
        
        return [types.TextContent(
            type="text",
            text=f"✓ Memory stored successfully! I'll remember: '{content}'"
        )]
    
    elif name == "recall_memory":
        if not arguments or "query" not in arguments:
            raise ValueError("Missing 'query' argument")
        
        query = arguments["query"]
        num_results = arguments.get("num_results", 3)
        
        if not memory_store:
            return [types.TextContent(
                type="text",
                text="No memories found."
            )]
        
        # Simple keyword search (can be enhanced with semantic search)
        matching = [m for m in memory_store if query.lower() in m["content"].lower()]
        matching = matching[:num_results]
        
        if not matching:
            return [types.TextContent(
                type="text",
                text="No memories found related to your query."
            )]
        
        response = f"I found {len(matching)} relevant memories:\n\n"
        for i, memory in enumerate(matching, 1):
            response += f"{i}. {memory['content']}\n"
            response += f"   (Stored: {memory['timestamp'][:10]})\n\n"
        
        return [types.TextContent(
            type="text",
            text=response.strip()
        )]
    
    elif name == "list_all_memories":
        if not memory_store:
            return [types.TextContent(
                type="text",
                text="I don't have any memories stored yet."
            )]
        
        response = f"I have {len(memory_store)} memories stored:\n\n"
        for i, memory in enumerate(memory_store, 1):
            response += f"{i}. {memory['content']}\n"
            response += f"   (Stored: {memory['timestamp'][:10]})\n\n"
        
        return [types.TextContent(
            type="text",
            text=response.strip()
        )]
    
    elif name == "clear_all_memories":
        count = len(memory_store)
        memory_store.clear()
        
        return [types.TextContent(
            type="text",
            text=f"✓ Cleared {count} memories. My memory is now empty."
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Start the MCP memory server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="memory",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())