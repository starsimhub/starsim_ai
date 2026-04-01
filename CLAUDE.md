# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Starsim-AI provides AI agents, skills, and tools for [Starsim](https://github.com/starsimhub/starsim), an agent-based disease modeling framework. Built on [mcp_pack](https://github.com/krosenfeld-IDM/mcp-pack), it exposes MCP (Model Context Protocol) servers that serve documentation for Starsim and its dependency Sciris.

Starsim documentation is also available on Context7: https://context7.com/starsimhub/starsim

## Repository Structure

- `plugins/starsim/` - Claude Code plugin for Starsim (MCP tools and 23 modeling/style skills). See `plugins/starsim/README.md` for full layout.
- `plugins/disease_modeling/` - Claude Code plugin for general disease modeling (WIP).
- `deploy_mcp_pack/` - MCP server deployment scripts. The `deploy` script creates databases from GitHub repos and starts SSE servers.
- `.claude-plugin/` - Root marketplace definition listing both plugins.
- `.github/workflows/main.yml` - CI/CD pipeline that deploys MCP servers to a remote VM via SSH.
- `internal/` - Scripts used for creating the AI tools (not user-facing).

## MCP Servers (legacy)

Two MCP servers (starsim on port 8001, sciris on port 8002) are deployed via `deploy_mcp_pack/` using SSE transport at `http://mcp.starsim.org:{port}`. Deploy locally with `cd deploy_mcp_pack && uv run python deploy`. CI/CD (`.github/workflows/main.yml`) deploys to a remote VM on push to `test` or manual dispatch.

## Versioning

When updating a plugin's version in its `plugin.json`, also update the corresponding `version` field in `.claude-plugin/marketplace.json` to match. The marketplace lists all plugins and their versions must stay in sync with the individual plugin definitions:

| Plugin            | plugin.json location                                  |
|-------------------|-------------------------------------------------------|
| starsim-ai        | `plugins/starsim/.claude-plugin/plugin.json`          |
| disease-modeling  | `plugins/disease_modeling/.claude-plugin/plugin.json`  |
| project-improver  | `plugins/project-improver/.claude-plugin/plugin.json` |

The version number is also often listed in `SKILL.md` and `CHANGELOG.md`. Make sure these are updated too.

## Tooling

- **Package manager**: `uv` (used for all Python execution via `uv run`)
- **License**: MIT
