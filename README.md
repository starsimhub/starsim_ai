# Starsim-AI

Starsim-aware AI agents, skills, and tools.


## Claude/Cursor plugin

Instructions coming soon!

## Context7

Starsim is available on [Context7](https://context7.com):

https://context7.com/starsimhub/starsim


## Manual MCP usage

Built on [mcp_pack](https://github.com/krosenfeld-IDM/mcp-pack).

Copy the following into `settings.json`, or into `mcp.json` for VS Code, Cursor, Claude, etc.:
```
    "mcp": {
        "servers": {
            "starsim": {
                "type": "sse",
                "url": "http://mcp.starsim.org:8001"
            },
            "sciris": {
                "type": "sse",
                "url": "http://mcp.starsim.org:8002"
            }
        }
    }
```

These agents should now be available to your IDE.

To use these tools in Claude Code, you can also use the following commands:
```
claude mcp add --transport sse starsim http://mcp.starsim.org:8001/sse
claude mcp add --transport sse sciris http://mcp.starsim.org:8002/sse
```
