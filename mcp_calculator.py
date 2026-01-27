"""
Calculator MCP Server
A standalone server that evaluates mathematical expressions via MCP protocol
"""

import asyncio
import json
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import mcp.types as types

# Create the MCP server instance with a name
server = Server("calculator-server")

# Define what happens when server starts
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    This function tells the MCP client what tools are available.
    It returns a list of tools this server provides.
    """
    return [
        types.Tool(
            name="calculate",
            description="Evaluates mathematical expressions like '5 + 3' or '(10 * 2) / 4'",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The math expression to evaluate (e.g., '5 + 3', '10 * 2')",
                    }
                },
                "required": ["expression"],
            },
        )
    ]

# Define what happens when the tool is called
@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    This function handles the actual calculation when the tool is called.
    
    Args:
        name: The tool name (should be "calculate")
        arguments: Dictionary containing the "expression" to evaluate
    
    Returns:
        List containing the result as text
    """
    
    # Check if the correct tool was called
    if name != "calculate":
        raise ValueError(f"Unknown tool: {name}")
    
    # Get the expression from arguments
    if not arguments or "expression" not in arguments:
        raise ValueError("Missing 'expression' argument")
    
    expression = arguments["expression"]
    
    try:
        # Validate the expression - only allow safe math characters
        allowed_chars = set('0123456789+-*/.() ')
        if not all(char in allowed_chars for char in expression):
            raise ValueError("Expression contains invalid characters. Only numbers and math operators allowed.")
        
        # Evaluate the expression
        result = eval(expression)
        
        # Return the result as text
        return [
            types.TextContent(
                type="text",
                text=str(result)
            )
        ]
    
    except ZeroDivisionError:
        # Handle division by zero
        return [
            types.TextContent(
                type="text",
                text="Error: Division by zero"
            )
        ]
    
    except Exception as e:
        # Handle any other errors
        return [
            types.TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )
        ]

# Main function to run the server
async def main():
    """
    Starts the MCP server and runs it via stdio (standard input/output).
    This allows the server to communicate with MCP clients.
    """
    
    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="calculator",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

# Entry point - run the server when this file is executed
if __name__ == "__main__":
    asyncio.run(main())