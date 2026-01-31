"""
MCP Tools Configuration
Maps your tools to existing MCP servers
"""

# MCP Server mapping for your tools
MCP_SERVERS = {
    "calculator": {
        "package": "@prajwalaswar/calculator-mcp",
        "enabled": True,
        "replaces": "calculator"
    },
    "weather": {
        "package": "@timlukahorstmann/mcp-weather",
        "enabled": True,  # ENABLED: Using wttr.in (no API key needed)
        "replaces": "get_weather"
    },
    "wikipedia": {
        "package": "@modelcontextprotocol/server-brave-search",
        "enabled": False,
        "requires_env": "BRAVE_API_KEY",
        "replaces": "search_wikipedia"
    },
    "google_search": {
        "package": "@modelcontextprotocol/server-brave-search",
        "enabled": False,
        "requires_env": "BRAVE_API_KEY",
        "replaces": "google_search"
    },
    "web_scraper": {
        "package": "@modelcontextprotocol/server-puppeteer",
        "enabled": False,
        "replaces": "web_scraper"
    },
    "gmail": {
        "package": "@modelcontextprotocol/server-gmail",
        "enabled": False,  # DISABLED: Timeout issues with SMTP in MCP context
        "replaces": "send_email"
    },
    "memory": {
        "package": "@modelcontextprotocol/server-memory",
        "enabled": False,  # DISABLED: Using regular ChromaDB memory instead
        "replaces": "store_memory, recall_memory, list_all_memories, clear_all_memories"
    }
}