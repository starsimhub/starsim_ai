# Starsim AI

Starsim-aware AI agents, built on [mcp_pack](https://github.com/krosenfeld-IDM/mcp-pack).

## Usage

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

## For developers

Users shouldn't need to do this -- this is just for developers to start their own server.

To start the server, run `deploy`.

To monitor:
- Check logs: `tail -f starsim.log`
- Check if running: `ps -p $(cat server_pids.txt | cut -d: -f2)`
- Stop servers: `kill $(cat server_pids.txt | cut -d: -f2)`
