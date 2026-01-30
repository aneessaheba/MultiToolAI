"""
Weather MCP Server
Simple weather tool using wttr.in (no API key needed)
"""

import asyncio
import requests
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import mcp.types as types

# Create the MCP server instance
server = Server("weather-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available weather tools"""
    return [
        types.Tool(
            name="get_weather",
            description="Get current weather for a city using wttr.in",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name (e.g., 'London', 'San Jose')"
                    }
                },
                "required": ["city"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    """Handle weather tool call"""
    
    if name != "get_weather":
        raise ValueError(f"Unknown tool: {name}")
    
    if not arguments or "city" not in arguments:
        raise ValueError("Missing 'city' argument")
    
    city = arguments["city"]
    
    try:
        # Use wttr.in - free weather service, no API key needed
        url = f"http://wttr.in/{city}?format=%C+%t"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        weather_info = response.text.strip()
        result = f"Weather in {city}: {weather_info}"
        
        return [types.TextContent(
            type="text",
            text=result
        )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error: Failed to get weather - {str(e)}"
        )]

async def main():
    """Start the MCP weather server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="weather",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())