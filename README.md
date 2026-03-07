# Starsim-AI

Starsim-aware AI agents, skills, and tools.


## Claude Code Plugins

This repo contains two Claude Code plugins, installable via the built-in marketplace:

- **starsim-ai** (`plugins/starsim/`) — Starsim and Sciris MCP tools and modeling skills
- **disease-modeling** (`plugins/disease_modeling/`) — General disease modeling skills and tools

To install, add this repo as a marketplace inside Claude Code:

```
/plugin marketplace add /path/to/starsim_ai
```

Then install either plugin from the **Discover** tab (`/plugin`).

## MCP servers

### Automatic MCP servers

Starsim is available on [Context7](https://context7.com):

https://context7.com/starsimhub/starsim

It is also available on [GitMCP](https://gitmcp.io):

https://gitmcp.io/starsimhub/starsim


### Manual MCP usage

> [!WARNING]
> Manual MCP servers may not be up to date; GitMCP or Context7 is recommended.

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

## Repo structure

- `deploy_mcp_pack`: Scripts for manually deploying the Starsim MCP server
- `internal`: Scripts used for creating the AI tools (not for the user)
- `plugins`: Claude Code skills and plugins