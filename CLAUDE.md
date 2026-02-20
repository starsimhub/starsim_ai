# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Starsim-AI provides AI agents, skills, and tools for [Starsim](https://github.com/starsimhub/starsim), an agent-based disease modeling framework. Built on [mcp_pack](https://github.com/krosenfeld-IDM/mcp-pack), it exposes MCP (Model Context Protocol) servers that serve documentation for Starsim and its dependency Sciris.

Starsim documentation is also available on Context7: https://context7.com/starsimhub/starsim

## Repository Structure

- `deploy_mcp_pack/` - MCP server deployment scripts. The `deploy` script creates databases from GitHub repos and starts SSE servers.
- `claude_plugin/` - Claude Code plugin for Starsim (WIP).
- `.github/workflows/main.yml` - CI/CD pipeline that deploys MCP servers to a remote VM via SSH.

## MCP Servers

Two MCP servers are deployed, both using SSE transport:

| Library  | Port | GitHub Repo                              |
|----------|------|------------------------------------------|
| starsim  | 8001 | https://github.com/starsimhub/starsim    |
| sciris   | 8002 | https://github.com/sciris/sciris          |

Public endpoints: `http://mcp.starsim.org:{port}`

## Key Commands

### Deploy MCP servers locally
```bash
cd deploy_mcp_pack && uv run python deploy
```
This creates documentation databases from the GitHub repos then starts both servers in the background.

### Monitor running servers
```bash
tail -f deploy_mcp_pack/starsim.log
tail -f deploy_mcp_pack/sciris.log
ps -p $(cat deploy_mcp_pack/server_pids.txt | cut -d: -f2)
```

### Stop servers
```bash
kill $(cat deploy_mcp_pack/server_pids.txt | cut -d: -f2)
```

### Add MCP servers to Claude Code
```bash
claude mcp add --transport sse starsim http://mcp.starsim.org:8001/sse
claude mcp add --transport sse sciris http://mcp.starsim.org:8002/sse
```

## CI/CD

The GitHub Actions workflow (`.github/workflows/main.yml`) triggers on push to `test` branch or manual dispatch. It SSHs into a remote VM, pulls the specified branch of `mcp-pack`, recreates databases, and restarts both MCP servers. Required secrets: `SSH_KEY`, `VM_USER`, `VM_HOST`, `GITHUB_TOKEN`, `OPENAI_API_KEY`.

## Tooling

- **Package manager**: `uv` (used for all Python execution via `uv run`)
- **License**: MIT
