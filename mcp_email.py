"""
Email MCP Server
Send emails using Gmail SMTP
"""

import asyncio
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import mcp.types as types

load_dotenv()

# Create the MCP server instance
server = Server("email-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available email tools"""
    return [
        types.Tool(
            name="send_email",
            description="Send an email via Gmail SMTP",
            inputSchema={
                "type": "object",
                "properties": {
                    "to_email": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content"
                    }
                },
                "required": ["to_email", "subject", "body"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    """Handle email sending"""
    
    if name != "send_email":
        raise ValueError(f"Unknown tool: {name}")
    
    if not arguments:
        raise ValueError("Missing arguments")
    
    to_email = arguments.get("to_email")
    subject = arguments.get("subject")
    body = arguments.get("body")
    
    if not all([to_email, subject, body]):
        raise ValueError("Missing required fields: to_email, subject, body")
    
    try:
        from_email = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("EMAIL_PASSWORD")
        
        if not from_email or not password:
            return [types.TextContent(
                type="text",
                text="Error: Email not configured. Set EMAIL_ADDRESS and EMAIL_PASSWORD in .env"
            )]
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Send via Gmail SMTP
        server_smtp = smtplib.SMTP('smtp.gmail.com', 587)
        server_smtp.starttls()
        server_smtp.login(from_email, password)
        server_smtp.send_message(msg)
        server_smtp.quit()
        
        return [types.TextContent(
            type="text",
            text=f"✓ Email sent successfully to {to_email}"
        )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error: Failed to send email - {str(e)}"
        )]

async def main():
    """Start the MCP email server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="email",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())