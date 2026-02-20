# Claude Starsim Plugin

A Claude Code plugin that provides Starsim and Sciris MCP tools and modeling skills.

## What's included

- **MCP servers** - Connects to the hosted Starsim and Sciris documentation servers, giving Claude access to up-to-date API docs and examples.
- **starsim-modeling skill** - Activates when building Starsim simulations (diseases, networks, interventions, etc.).
- **sciris-utilities skill** - Activates when using Sciris utilities (file I/O, parallelization, data structures, etc.).

## Installation

### Option 1: Add from local path

```bash
claude plugin add /path/to/starsim_ai/claude_plugin
```

### Option 2: Add from GitHub

```bash
claude plugin add https://github.com/starsimhub/starsim_ai --path claude_plugin
```

### Verify installation

```bash
claude /mcp
```

You should see `starsim` and `sciris` MCP servers listed.

## Plugin structure

```
claude_plugin/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── .mcp.json                # MCP server definitions (starsim + sciris)
├── skills/
│   ├── starsim-modeling/
│   │   └── SKILL.md         # Starsim simulation guidance
│   └── sciris-utilities/
│       └── SKILL.md         # Sciris utility guidance
└── README.md
```
